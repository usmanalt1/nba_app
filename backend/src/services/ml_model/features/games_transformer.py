from services.ml_model.features.transformer_base import TransformerBase
import pandas as pd
from config.logger import get_logger


class GamesTransformer(TransformerBase):
    def __init__(self, df_games: pd.DataFrame):
        self.df_games = df_games
        self.logger  = get_logger(__name__)

    def transform(self):
        try:
            self.logger.info("Applying dim_games transformer")
            self.df_games = self.df_games[["game_id", "season_id", "game_date", "home_team_id", "away_team_id", "home_pts", "away_pts", "home_wl"]]
            self.df_games = self.df_games.drop_duplicates()
            self.df_games["game_date"] = pd.to_datetime(self.df_games["game_date"])
        except Exception as e:
            self.logger.error(f"Error when transforming dim_games: {e}")
            raise

        return self._home_away_features(df_games=self.df_games)
    
    def _home_away_features(self, df_games: pd.DataFrame) -> pd.DataFrame:
        home = df_games.rename(columns={"home_team_id": "team_id", "away_team_id": "opponent_id", "home_wl": "wl"})
        home["is_home"] = 1
        home = home[["game_id", "season_id", "game_date", "team_id", "opponent_id", "wl", "is_home"]]

        away = df_games.rename(columns={"away_team_id": "team_id", "home_team_id": "opponent_id"})
        away["wl"] = away["home_wl"].map({"W": "L", "L": "W"})
        away["is_home"] = 0
        away = away[["game_id", "season_id", "game_date", "team_id", "opponent_id", "wl", "is_home"]]

        team_games = pd.concat([home, away], ignore_index=True)
        team_games["team_win"] = (team_games["wl"] == "W").astype(int)

        return team_games

        