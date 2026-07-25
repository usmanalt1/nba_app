from services.ml_model.features.transformer_base import TransformerBase
import pandas as pd

from config.logger import get_logger


class BoxscoreTransformer(TransformerBase):
    def __init__(self, df_boxscore: pd.DataFrame, df_games: pd.DataFrame):
        self.df_boxscore = df_boxscore
        self.df_games = df_games
        self.logger = get_logger(__name__)


    def transform(self):
        self.logger.info("Transform Apply Boxscore...")
        try:
            self.df_boxscore = self._processs_games_df()
            boxscore_df = self._build_boxscore_df(df_games=self.df_games, df_boxscore=self.df_boxscore)
            boxscore_df = self._build_rolling_avg(df_boxscore=boxscore_df)
            boxscore_df = self._build_differential(df_boxscore=boxscore_df)

            self.logger.info("Transform Apply Boxscore Done...")
        except Exception as e:
            self.logger.error(f"Error in transforming boxscore: {e}")
            raise

        return boxscore_df


    def _processs_games_df(self):
        return self.df_boxscore[["season_id", "team_id", "game_id", "min", "fgm", "fga", "fg_pct", "fg3m", "fg3a", "fg3_pct",
           "ftm", "fta", "ft_pct", "oreb", "dreb", "reb", "ast", "stl", "blk", "tov", "pf", "pts", "plus_minus"]]
    
    def _build_boxscore_df(self, df_games: pd.DataFrame, df_boxscore: pd.DataFrame) -> pd.DataFrame:
        df_boxscore = df_games.merge(df_boxscore, on=["season_id", "team_id", "game_id"], how="left")
        df_boxscore = df_boxscore.sort_values(["team_id", "season_id", "game_date"]).reset_index(drop=True)
        df_boxscore["days_rest"] = df_boxscore.groupby(["team_id", "season_id"])["game_date"].diff().dt.days
        df_boxscore["b2b"] = (df_boxscore["days_rest"] <= 1).astype("Int64")

        return df_boxscore

    def _build_rolling_avg(self, df_boxscore: pd.DataFrame) -> pd.DataFrame:
        # season-to-date "form" - shift(1) FIRST so the current game's own box score is never
        # part of its own feature, then expanding().mean() over what's left (resets each season).
        stat_cols = ["fg_pct", "fg3_pct", "ft_pct", "reb", "oreb", "dreb",
                    "ast", "stl", "blk", "tov", "pts", "plus_minus"]

        grp_keys = ["team_id", "season_id"]
        shifted = df_boxscore.groupby(grp_keys)[stat_cols + ["team_win"]].shift(1)
        rolling_avg = shifted.groupby([df_boxscore["team_id"], df_boxscore["season_id"]]).expanding().mean()
        rolling_avg = rolling_avg.reset_index(level=[0, 1], drop=True)
        rolling_avg.columns = [f"pre_{c}" for c in rolling_avg.columns]
        rolling_avg = rolling_avg.rename(columns={"pre_team_win": "pre_win_pct"})

        df_boxscore = pd.concat([df_boxscore, rolling_avg], axis=1)

        # first game of each team's season has no prior history - these will be dropped later
        df_boxscore["pre_win_pct"].isna().sum()

        return df_boxscore
    
    def _build_differential(self, df_boxscore: pd.DataFrame) -> pd.DataFrame:
        feature_cols = ["days_rest", "b2b"] + [c for c in df_boxscore.columns if c.startswith("pre_")]
        home_feat = df_boxscore[df_boxscore.is_home == 1][["game_id", "season_id"] + feature_cols + ["team_win"]].copy()
        home_feat.columns = ["game_id", "season_id"] + [f"home_{c}" for c in feature_cols] + ["home_win"]

        away_feat = df_boxscore[df_boxscore.is_home == 0][["game_id"] + feature_cols].copy()
        away_feat.columns = ["game_id"] + [f"away_{c}" for c in feature_cols]

        final_boxscore_df = home_feat.merge(away_feat, on="game_id", how="inner")

        diff_cols = []
        for c in feature_cols:
            final_boxscore_df[f"diff_{c}"] = final_boxscore_df[f"home_{c}"] - final_boxscore_df[f"away_{c}"]
            diff_cols.append(f"diff_{c}")

        # drop games where either team has no history yet (first game(s) of a season)
        before = len(final_boxscore_df)
        final_boxscore_df = final_boxscore_df.dropna(subset=diff_cols).reset_index(drop=True)
        print(f"dropped {before - len(final_boxscore_df)} rows with no prior-game history, {len(final_boxscore_df)} remain")
        print("home win rate in modeling set:", final_boxscore_df["home_win"].mean())

        return final_boxscore_df

        
