import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, log_loss, brier_score_loss, roc_auc_score
import pandas as pd

from services.ml_model.models.models_base import ModelBase
from services.ml_model.models.model_config import ModelsConfig
from services.ml_model.models.train_result import TrainResult
from services.ml_model.models.models_strategy import STRATEGY_REGISTRY
from services.db.db_service import DBService
from services.ml_model.features.boxscore_transformer import BoxscoreTransformer
from services.ml_model.features.games_transformer import GamesTransformer
from services.ml_model.features.players_transfomer import PlayersTransformer
from config.logger import get_logger

logger = get_logger(__name__)
SEASON_TOTAL_GAMES = 82


def _report(name, y_true, pred, proba) -> dict[str, float]:
    metrics = {
        "accuracy": accuracy_score(y_true, pred),
        "log_loss": log_loss(y_true, proba, labels=[0, 1]),
        "brier": brier_score_loss(y_true, proba),
        "auc": roc_auc_score(y_true, proba),
    }
    logger.info(
        f"{name:20s} acc={metrics['accuracy']:.3f}  logloss={metrics['log_loss']:.3f}  "
        f"brier={metrics['brier']:.3f}  auc={metrics['auc']:.3f}"
    )
    return metrics


class ModelTraner(ModelBase):
    def __init__(self, strategy: str, season: str):
        if strategy not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy: {strategy}")

        self.db_service = DBService()
        self.df_games, self.df_team_stats, self.df_player_stats = self.load_data()
        self.season = season

        SEASON_MAPPING = {
            "2025-26": 22025
        }
        self.test_filter = SEASON_MAPPING.get(self.season, None)
        if not self.test_filter:
            raise ValueError("No Season Filter...")

        games_transformer = GamesTransformer(df_games=self.df_games)
        team_games_df = games_transformer.transform()

        boxscore_transformer = BoxscoreTransformer(df_games=team_games_df, df_boxscore=self.df_team_stats)
        boxscore_model_df = boxscore_transformer.transform()

        self.config = ModelsConfig(
            target_col="home_win",
            test_filter=self.test_filter,
            transformers=[
                games_transformer,
                boxscore_transformer,
                PlayersTransformer(
                    model_df=boxscore_model_df,
                    df_player_stats=self.df_player_stats,
                    df_games=self.df_games,
                ),
            ],
            model=STRATEGY_REGISTRY[strategy](),
        )
        self.scaler = StandardScaler()

    def load_data(self):
        df_games = self.db_service.read("dim_games")
        df_team_stats = self.db_service.read("fct_team_stats")
        df_player_stats = self.db_service.read("fct_player_stats")

        return df_games, df_team_stats, df_player_stats

    def build(self):
        for t in self.config.transformers:
            model_df = t.transform()

        test_season = self.config.test_filter
        diff_cols = [c for c in model_df.columns if c.startswith("diff_")]

        train_df = model_df[model_df["season_id"].astype(int) < test_season]
        test_df = model_df[model_df["season_id"].astype(int) == test_season].reset_index(drop=True)

        target_col = self.config.target_col
        X_train, y_train = train_df[diff_cols], train_df[target_col]
        X_test, y_test = test_df[diff_cols], test_df[target_col]
        test_ids = test_df[["game_id", "season_id"]]

        logger.info(f"train: {X_train.shape}  test: {X_test.shape}")

        return X_train, y_train, X_test, y_test, test_ids

    def train(self) -> TrainResult:
        X_train, y_train, X_test, y_test, test_ids = self.build()

        # naive baseline: always predict the home team wins (home court advantage is real -
        # any model needs to beat this, not just beat 50/50, to be worth anything)
        naive_pred = np.ones(len(y_test))
        naive_proba = np.full(len(y_test), y_train.mean())
        _report("naive (home always)", y_test, naive_pred, naive_proba)

        # logistic regression needs scaled inputs since features are on very different scales
        # (fg_pct is ~0-1, pts is ~0-30, plus_minus is ~-15 to 15)
        X_train_s = self.scaler.fit_transform(X_train)
        X_test_s = self.scaler.transform(X_test)

        model = self.config.model
        model.fit(X_train_s, y_train)
        proba = model.predict_proba(X_test_s)[:, 1]
        pred = (proba >= 0.5).astype(int)
        metrics = _report(type(model).__name__, y_test, pred, proba)

        predictions = test_ids.copy()
        predictions["actual_home_win"] = y_test.values
        predictions["home_win_probability"] = proba
        predictions["predicted_home_win"] = pred.astype(bool)

        predictions = predictions.merge(self.df_games[["game_id", "game_date", "home_team_name", "away_team_name", "season"]], on="game_id")
        predictions["matchup"] = predictions["home_team_name"] + " vs " + predictions["away_team_name"]
        predictions["predicted_winner"] = np.where(
            predictions["predicted_home_win"], predictions["home_team_name"], predictions["away_team_name"]
        )
        predicted_df: pd.DataFrame = predictions["predicted_winner"].value_counts().reset_index()
        predicted_df = predicted_df.rename(columns={"count": "wins"})
        predicted_df["loss"] = SEASON_TOTAL_GAMES - predicted_df["wins"]
        predicted_df["season"] = self.season
        predicted_df.rename(columns={"predicted_winner": "team"}, inplace=True)


        return TrainResult(model=model, metrics=metrics, predictions=predictions, season_record=predicted_df)
