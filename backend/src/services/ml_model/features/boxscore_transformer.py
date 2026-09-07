"""Create rolling team box-score features and game differentials for modeling."""

import pandas as pd

from services.ml_model.features.transformer_base import TransformerBase
from config.logger import get_logger

SHRINKAGE_GAMES = 10

STAT_COLS = ["fg_pct", "fg3_pct", "ft_pct", "reb", "oreb", "dreb",
             "ast", "stl", "blk", "tov", "pts", "plus_minus"]


class BoxscoreTransformer(TransformerBase):
    """Build team form features from box-score history and merge them by game."""

    def __init__(self, df_boxscore: pd.DataFrame, df_games: pd.DataFrame):
        self.df_boxscore = df_boxscore
        self.df_games = df_games
        self.logger = get_logger(__name__)

    def transform(self) -> pd.DataFrame:
        self.logger.info("Transform Apply Boxscore...")
        try:
            self.df_boxscore = self._select_boxscore_columns()
            boxscore_df = self._build_boxscore_df(df_games=self.df_games, df_boxscore=self.df_boxscore)
            boxscore_df = self._build_rolling_avg(df_boxscore=boxscore_df)
            boxscore_df = self._build_differential(df_boxscore=boxscore_df)

            self.logger.info("Transform Apply Boxscore Done...")
        except Exception as e:
            self.logger.error(f"Error in transforming boxscore: {e}")
            raise

        return boxscore_df

    def _select_boxscore_columns(self) -> pd.DataFrame:
        """Keep only the columns needed for rolling team-form features."""
        return self.df_boxscore[
            [
                "season_id", "team_id", "game_id", "min", "fgm", "fga", "fg_pct", "fg3m", "fg3a",
                "fg3_pct", "ftm", "fta", "ft_pct", "oreb", "dreb", "reb", "ast", "stl", "blk",
                "tov", "pf", "pts", "plus_minus",
            ]
        ]

    def _build_boxscore_df(self, df_games: pd.DataFrame, df_boxscore: pd.DataFrame) -> pd.DataFrame:
        """Merge box-score rows onto schedule data and add rest/b2b indicators."""
        merged = df_games.merge(df_boxscore, on=["season_id", "team_id", "game_id"], how="left")
        merged = merged.sort_values(["team_id", "season_id", "game_date"]).reset_index(drop=True)
        merged["days_rest"] = merged.groupby(["team_id", "season_id"])["game_date"].diff().dt.days
        merged["b2b"] = (merged["days_rest"] <= 1).astype("Int64")

        return merged

    def _build_prior_season_baseline(self, df_boxscore: pd.DataFrame) -> pd.DataFrame:
        """Compute each team's last-season average to use as a fallback when this season is thin."""
        prior_cols = [f"prior_{c}" for c in STAT_COLS] + ["prior_win_pct"]

        season_avg = (
            df_boxscore.groupby(["team_id", "season_id"])[STAT_COLS + ["team_win"]]
            .mean()
            .reset_index()
            .rename(columns={c: f"prior_{c}" for c in STAT_COLS})
            .rename(columns={"team_win": "prior_win_pct"})
            .sort_values(["team_id", "season_id"])
        )
        season_avg[prior_cols] = season_avg.groupby("team_id")[prior_cols].shift(1)

        coverage = season_avg["prior_win_pct"].notna().mean()
        self.logger.info(f"Prior-season baseline available for {coverage:.1%} of team-seasons")

        return season_avg[["team_id", "season_id"] + prior_cols]

    def _build_rolling_avg(self, df_boxscore: pd.DataFrame) -> pd.DataFrame:
        """Build each team's season-to-date rolling form and blend it with the prior-season baseline."""
        grp_keys = ["team_id", "season_id"]
        shifted = df_boxscore.groupby(grp_keys)[STAT_COLS + ["team_win"]].shift(1)
        games_so_far = df_boxscore.groupby(grp_keys).cumcount()

        season_to_date = shifted.groupby([df_boxscore["team_id"], df_boxscore["season_id"]]).expanding().mean()
        season_to_date = season_to_date.reset_index(level=[0, 1], drop=True)
        season_to_date.columns = [f"this_season_{c}" for c in season_to_date.columns]
        season_to_date = season_to_date.rename(columns={"this_season_team_win": "this_season_win_pct"})

        df_boxscore = pd.concat([df_boxscore, season_to_date], axis=1)
        df_boxscore = df_boxscore.merge(
            self._build_prior_season_baseline(df_boxscore), on=["team_id", "season_id"], how="left"
        )

        blend_specs = [(c, f"this_season_{c}", f"prior_{c}") for c in STAT_COLS]
        blend_specs.append(("win_pct", "this_season_win_pct", "prior_win_pct"))

        for out_col, this_season_col, prior_col in blend_specs:
            this_val = df_boxscore[this_season_col]
            prior_val = df_boxscore[prior_col]
            blended = (games_so_far * this_val.fillna(0) + SHRINKAGE_GAMES * prior_val) / (games_so_far + SHRINKAGE_GAMES)
            df_boxscore[f"pre_{out_col}"] = blended.where(prior_val.notna(), this_val)

        still_missing = df_boxscore["pre_win_pct"].isna().sum()
        self.logger.info(f"{still_missing} rows have no this-season or prior-season history - will be dropped downstream")

        return df_boxscore

    def _build_differential(self, df_boxscore: pd.DataFrame) -> pd.DataFrame:
        """Convert the per-team features into home-vs-away differentials for modeling."""
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

        before = len(final_boxscore_df)
        final_boxscore_df = final_boxscore_df.dropna(subset=diff_cols).reset_index(drop=True)
        self.logger.info(f"dropped {before - len(final_boxscore_df)} rows with no prior-game history, {len(final_boxscore_df)} remain")
        self.logger.info(f"home win rate in modeling set: {final_boxscore_df['home_win'].mean():.3f}")

        return final_boxscore_df
