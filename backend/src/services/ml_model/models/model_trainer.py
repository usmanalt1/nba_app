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
from services.ml_model.features.playoff_boxscore_transformer import PlayoffBoxscoreTransformer
from services.ml_model.features.games_transformer import GamesTransformer
from services.ml_model.features.players_transfomer import PlayersTransformer
from config.logger import get_logger

logger = get_logger(__name__)

MODE_BACKTEST = "backtest"
MODE_LIVE = "live"

SEASON_TYPE_PLAYOFFS = "playoffs"
SEASON_TYPE_REGULAR = "regular"
SEASON_TYPE_PRESEASON = "preseason"

# Season types predicted from a different type's games. Preseason has no history to
# train on, so it is predicted off regular-season form.
TRAIN_SEASON_TYPE = {SEASON_TYPE_PRESEASON: SEASON_TYPE_REGULAR}


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
    def __init__(self, strategy: str, season: str, season_type: str, mode: str = MODE_BACKTEST):
        """
        Trains `strategy` and produces predictions for `season`/`season_type`.

        mode="backtest" (default) treats `season` as a completed season: the model trains
        on every other season and is scored against all of `season`'s games.

        mode="live" treats `season` as the season currently in progress: the model trains
        on every other season plus whatever games in `season` already have a recorded
        result (home_wl not null), then produces probabilities for the remaining, unplayed
        games. There's no outcome to score those against yet, so metrics come back empty.
        """
        if strategy not in STRATEGY_REGISTRY:
            raise ValueError(f"Unknown strategy: {strategy}")
        if mode not in (MODE_BACKTEST, MODE_LIVE):
            raise ValueError(f"Unknown mode: {mode}")

        logger.info(
            f"Initialising ModelTrainer with strategy={strategy}, season={season}, "
            f"season_type={season_type}, mode={mode}"
        )

        self.db_service = DBService()
        self.season = season
        self.season_type = season_type
        self.mode = mode
        all_games, all_team_stats, all_player_stats, self.df_teams = self.load_data()

        self.train_season_type = TRAIN_SEASON_TYPE.get(season_type, season_type)
        self._select_frames(all_games, all_team_stats, all_player_stats)
        self.predicted_game_ids = self._select_predicted_games()

        if self.season_type == SEASON_TYPE_PLAYOFFS:
            transformers = self._build_playoff_transformers(all_games, all_team_stats, all_player_stats)
        else:
            transformers = self._build_regular_transformers()

        self.data_warnings = self._validate_season_completeness()

        self.config = ModelsConfig(
            target_col="home_win",
            test_filter=self.season,
            transformers=transformers,
            model=STRATEGY_REGISTRY[strategy](),
        )
        self.scaler = StandardScaler()

    def _select_frames(self, all_games, all_team_stats, all_player_stats) -> None:
        """Narrow the source frames to the season types this run needs."""
        frame_types = {self.season_type, self.train_season_type}
        if self.train_season_type != self.season_type:
            logger.info(
                f"Training on {self.train_season_type} games to predict {self.season_type} games"
            )

        self.df_games = all_games[all_games["season_type"].isin(frame_types)].copy()
        self.df_team_stats = all_team_stats[all_team_stats["season_type"].isin(frame_types)].copy()
        self.df_player_stats = all_player_stats[all_player_stats["season_type"].isin(frame_types)].copy()

    def _select_predicted_games(self) -> set:
        """Game ids this run predicts, pinned here because GamesTransformer drops
        season_type - downstream, season alone no longer identifies them."""
        predicted = self.df_games[
            (self.df_games["season"] == self.season)
            & (self.df_games["season_type"] == self.season_type)
        ]
        return set(predicted["game_id"])

    def load_data(self):
        df_games = self.db_service.read("dim_games")
        df_team_stats = self.db_service.read("fct_team_stats")
        df_player_stats = self.db_service.read("fct_player_stats")
        df_teams = self.db_service.read("dim_teams")

        return df_games, df_team_stats, df_player_stats, df_teams

    def _build_regular_transformers(self) -> list:
        games_transformer = GamesTransformer(df_games=self.df_games)
        team_games_df = games_transformer.transform()

        boxscore_transformer = BoxscoreTransformer(df_games=team_games_df, df_boxscore=self.df_team_stats)
        boxscore_model_df = boxscore_transformer.transform()

        return [
            games_transformer,
            boxscore_transformer,
            PlayersTransformer(
                model_df=boxscore_model_df,
                df_player_stats=self.df_player_stats,
                df_games=self.df_games,
            ),
        ]

    def _build_playoff_transformers(self, all_games: pd.DataFrame, all_team_stats: pd.DataFrame, all_player_stats: pd.DataFrame) -> list:
        regular_games = all_games[(all_games["season_type"] == SEASON_TYPE_REGULAR) & (all_games["season"] == self.season)].copy()
        regular_team_stats = all_team_stats[
            (all_team_stats["season_type"] == SEASON_TYPE_REGULAR) & (all_team_stats["season"] == self.season)
        ].copy()
        all_playoff_games = all_games[all_games["season_type"] == SEASON_TYPE_PLAYOFFS].copy()

        playoff_transformer = PlayoffBoxscoreTransformer(
            df_games=self.df_games,
            df_boxscore=self.df_team_stats,
            df_regular_games=regular_games,
            df_regular_boxscore=regular_team_stats,
            df_all_playoff_games=all_playoff_games,
        )
        boxscore_model_df = playoff_transformer.transform()

        # star ratings are built off regular-season performance only - a handful of
        # playoff games is too thin a sample to re-rank players against. Every playoff
        # team already has a full regular season on record, so feeding that in (across
        # all seasons, for PlayersTransformer's own cross-season baseline) plus this
        # season's playoff schedule appended (so there's a row to attach a rating to for
        # each playoff game) lets its existing season-to-date logic carry the
        # regular-season rating straight into the postseason, unmodified.
        regular_player_stats_all_seasons = all_player_stats[all_player_stats["season_type"] == SEASON_TYPE_REGULAR].copy()
        regular_games_all_seasons = all_games[all_games["season_type"] == SEASON_TYPE_REGULAR].copy()
        players_schedule = pd.concat([regular_games_all_seasons, self.df_games], ignore_index=True)

        return [
            playoff_transformer,
            PlayersTransformer(
                model_df=boxscore_model_df,
                df_player_stats=regular_player_stats_all_seasons,
                df_games=players_schedule,
            ),
        ]

    def _played_game_ids(self) -> set:
        return set(self.df_games.loc[self.df_games["home_wl"].notna(), "game_id"])

    def _validate_season_completeness(self) -> list[str]:
        """Sanity-check that `self.season` looks fully played before treating it as
        finished. dim_games can be missing rows outright (an ingestion gap - see the
        OKC 2025-26 case: 81 rows instead of 82, not a modeling artifact) or contain
        rows for games that simply haven't been played yet (home_wl still null).
        Neither is visible from the model's own features, so both are checked directly
        against the raw schedule and surfaced as warnings rather than silently producing
        a skewed season_record - or, in backtest mode, letting an unplayed game
        masquerade as a home-team loss (GamesTransformer's wl == "W" check turns a null
        result into False, i.e. a "loss", same as it would for a real one)."""
        warnings = []
        season_games = self.df_games[
            (self.df_games["season"] == self.season)
            & (self.df_games["season_type"] == self.season_type)
        ]
        # a schedule slot with no real teams assigned yet (e.g. an in-season-tournament
        # knockout round not yet resolved) isn't a data gap - exclude it from both checks
        real_games = season_games[(season_games["home_team_id"] != 0) & (season_games["away_team_id"] != 0)]

        unplayed = real_games[real_games["home_wl"].isna()]
        if len(unplayed) > 0:
            warnings.append(
                f"{len(unplayed)} {self.season_type} game(s) in {self.season} have no recorded result yet "
                f"(e.g. {unplayed['game_id'].iloc[0]}) - excluded from evaluation rather than treated as a loss."
            )

        if self.season_type == SEASON_TYPE_REGULAR:
            counts = pd.concat([real_games["home_team_id"], real_games["away_team_id"]]).value_counts()
            if len(counts) > 0:
                expected = counts.max()
                short = counts[counts < expected]
                if len(short) > 0:
                    team_names = self.df_teams.drop_duplicates("team_id", keep="last").set_index("team_id")["team_name"]
                    details = ", ".join(f"{team_names.get(tid, tid)} ({n}/{expected})" for tid, n in short.items())
                    warnings.append(
                        f"{len(short)} team(s) have fewer than {expected} recorded {self.season} games - "
                        f"dim_games looks incomplete for them: {details}"
                    )

        for w in warnings:
            logger.warning(w)

        return warnings

    def build(self):
        for t in self.config.transformers:
            model_df = t.transform()

        # diff_ columns are home-vs-away differentials; round/game_in_series (playoffs
        # only) are shared context, not team-relative, so they're picked up separately
        diff_cols = [c for c in model_df.columns if c.startswith("diff_")]
        context_cols = [c for c in ("round", "game_in_series") if c in model_df.columns]
        feature_cols = diff_cols + context_cols
        target_col = self.config.target_col

        is_predicted = model_df["game_id"].isin(self.predicted_game_ids)

        is_played = model_df["game_id"].isin(self._played_game_ids())

        # is_played guards both sides: GamesTransformer's `wl == "W"` turns a null result
        # into False, so an unplayed game would train and score as a home defeat.
        if self.mode == MODE_BACKTEST:
            train_df = model_df[~is_predicted & is_played].reset_index(drop=True)
            eval_df = model_df[is_predicted & is_played].reset_index(drop=True)
            y_eval = eval_df[target_col]
        else:
            train_df = model_df[is_played].reset_index(drop=True)
            eval_df = model_df[is_predicted & ~is_played].reset_index(drop=True)
            y_eval = None

        X_train, y_train = train_df[feature_cols], train_df[target_col]
        X_eval = eval_df[feature_cols]
        eval_ids = eval_df[["game_id", "season"]]

        logger.info(f"train: {X_train.shape}  eval/predict ({self.mode}): {X_eval.shape}")

        return X_train, y_train, X_eval, y_eval, eval_ids

    def train(self) -> TrainResult:
        X_train, y_train, X_eval, y_eval, eval_ids = self.build()


        X_train_s = self.scaler.fit_transform(X_train)

        model = self.config.model
        model.fit(X_train_s, y_train)

        if len(X_eval) > 0:
            X_eval_s = self.scaler.transform(X_eval)
            proba = model.predict_proba(X_eval_s)[:, 1]
            pred = (proba >= 0.5).astype(int)
        else:
            # nothing left to predict (e.g. mode="live" against a fully-completed season)
            proba = np.array([])
            pred = np.array([], dtype=int)

        metrics = None
        if self.mode == MODE_BACKTEST:
            # naive baseline: always predict the home team wins (home court advantage is
            # real - any model needs to beat this, not just beat 50/50, to be worth anything)
            naive_pred = np.ones(len(y_eval))
            naive_proba = np.full(len(y_eval), y_train.mean())
            _report("naive (home always)", y_eval, naive_pred, naive_proba)
            metrics = _report(type(model).__name__, y_eval, pred, proba)
        else:
            logger.info(f"{type(model).__name__:20s} produced {len(pred)} predictions for unplayed {self.season} games")

        predictions = eval_ids.copy()
        predictions["actual_home_win"] = y_eval.values if y_eval is not None else None
        predictions["home_win_probability"] = proba
        predictions["predicted_home_win"] = pred.astype(bool)
        predictions["season"] = self.season
        predictions["season_type"] = self.season_type

        team_names = self.df_teams.drop_duplicates("team_id", keep="last").set_index("team_id")["team_name"]

        predictions = predictions.merge(self.df_games[["game_id", "game_date", "home_team_id", "away_team_id"]], on="game_id")
        predictions["home_team_name"] = predictions["home_team_id"].map(team_names)
        predictions["away_team_name"] = predictions["away_team_id"].map(team_names)
        predictions["matchup"] = predictions["home_team_name"] + " vs " + predictions["away_team_name"]
        predictions["predicted_winner"] = np.where(
            predictions["predicted_home_win"], predictions["home_team_name"], predictions["away_team_name"]
        )

        predicted_df: pd.DataFrame = predictions["predicted_winner"].value_counts().reset_index()
        predicted_df = predicted_df.rename(columns={"count": "wins"})
        games_seen = pd.concat([predictions["home_team_name"], predictions["away_team_name"]]).value_counts()
        predicted_df["loss"] = predicted_df["predicted_winner"].map(games_seen).fillna(0).astype(int) - predicted_df["wins"]
        predicted_df["season_type"] = self.season_type
        predicted_df["season"] = self.season
        predicted_df.rename(columns={"predicted_winner": "team"}, inplace=True)

        return TrainResult(model=model, metrics=metrics, predictions=predictions, season_record=predicted_df, warnings=self.data_warnings)
