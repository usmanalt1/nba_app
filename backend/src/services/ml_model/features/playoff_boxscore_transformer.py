"""Team-form features for playoff games.

Differs from BoxscoreTransformer in what "prior" means: a playoff team already has a
full, current-roster regular season on record this year, which is a much stronger prior
than a thin or missing prior *postseason* (most teams don't make the playoffs every
year, and a short series is a noisy sample even when they did). So the blend here is
[games played so far this postseason] vs [this same season's regular-season average],
not [this postseason] vs [last postseason].

Also adds series-context features (round, game-in-series, series score) that fall
straight out of the NBA's own game_id scheme, and a standalone prior-postseason-history
feature kept separate from the main form blend rather than folded into it - it's sparse
and often reflects a different roster, so it shouldn't dilute the same-season signal.
"""

import pandas as pd

from services.ml_model.features.transformer_base import TransformerBase
from services.ml_model.features.games_transformer import GamesTransformer
from config.logger import get_logger

SHRINKAGE_GAMES = 4
STAT_COLS = ["fg_pct", "fg3_pct", "ft_pct", "reb", "oreb", "dreb",
             "ast", "stl", "blk", "tov", "pts", "plus_minus"]


class PlayoffBoxscoreTransformer(TransformerBase):
    """Build playoff team-form features and merge them by game."""

    def __init__(
        self,
        df_games: pd.DataFrame,
        df_boxscore: pd.DataFrame,
        df_regular_games: pd.DataFrame,
        df_regular_boxscore: pd.DataFrame,
        df_all_playoff_games: pd.DataFrame,
    ):
        """
        df_games / df_boxscore: this season's playoff schedule and box scores.
        df_regular_games / df_regular_boxscore: this SAME season's regular-season
            schedule and box scores - the baseline.
        df_all_playoff_games: every season's playoff schedule (unfiltered by season) -
            used to build the prior-postseason-history feature.
        """
        self.df_games = df_games
        self.df_boxscore = df_boxscore
        self.df_regular_games = df_regular_games
        self.df_regular_boxscore = df_regular_boxscore
        self.df_all_playoff_games = df_all_playoff_games
        self.logger = get_logger(__name__)

    def transform(self) -> pd.DataFrame:
        self.logger.info("Transform Apply Playoff Boxscore...")
        try:
            team_games = GamesTransformer(df_games=self.df_games).transform()
            reg_team_games = GamesTransformer(df_games=self.df_regular_games).transform()
            all_playoff_team_games = GamesTransformer(df_games=self.df_all_playoff_games).transform()

            merged = self._build_boxscore_df(team_games)
            merged = self._add_series_context(merged)
            merged = self._build_rolling_avg(merged, reg_team_games)
            merged = self._add_playoff_history(merged, all_playoff_team_games)
            result = self._build_differential(merged)

            self.logger.info("Transform Apply Playoff Boxscore Done...")
        except Exception as e:
            self.logger.error(f"Error in transforming playoff boxscore: {e}")
            raise

        return result

    def _build_boxscore_df(self, team_games: pd.DataFrame) -> pd.DataFrame:
        """Merge box-score rows onto the playoff schedule and add a rest/b2b indicator."""
        boxscore_cols = ["season", "team_id", "game_id"] + STAT_COLS
        merged = team_games.merge(self.df_boxscore[boxscore_cols], on=["season", "team_id", "game_id"], how="left")
        merged = merged.sort_values(["team_id", "season", "game_date"]).reset_index(drop=True)
        merged["days_rest"] = merged.groupby(["team_id", "season"])["game_date"].diff().dt.days
        merged["days_rest"] = merged["days_rest"].fillna(merged["days_rest"].mean())
        merged["b2b"] = (merged["days_rest"] <= 1).astype("Int64")

        return merged

    def _add_series_context(self, merged: pd.DataFrame) -> pd.DataFrame:
        """round/game-in-series/series score come straight out of the NBA's own game_id
        scheme (e.g. "0042500161": chars[5:8] encode "00" + round, char[8] the matchup
        index within the round, char[9] the game number within that series) - no extra
        data needed."""
        merged["round"] = merged["game_id"].str[7].astype(int)
        merged["series_id"] = merged["game_id"].str[:9]
        merged["game_in_series"] = merged["game_id"].str[9].astype(int)

        merged = merged.sort_values(["series_id", "team_id", "game_in_series"]).reset_index(drop=True)
        shifted_wins = merged.groupby(["series_id", "team_id"])["team_win"].shift(1)
        merged["series_wins_so_far"] = shifted_wins.groupby([merged["series_id"], merged["team_id"]]).cumsum().fillna(0)

        return merged

    def _build_regular_season_baseline(self, reg_team_games: pd.DataFrame) -> pd.DataFrame:
        """This same season's regular-season average per team - the playoff baseline."""
        boxscore_cols = ["season", "team_id", "game_id"] + STAT_COLS
        merged = reg_team_games.merge(self.df_regular_boxscore[boxscore_cols], on=["season", "team_id", "game_id"], how="left")
        baseline = (
            merged.groupby(["team_id", "season"])[STAT_COLS + ["team_win"]].mean().reset_index()
            .rename(columns={c: f"prior_{c}" for c in STAT_COLS})
            .rename(columns={"team_win": "prior_win_pct"})
        )
        return baseline[["team_id", "season"] + [f"prior_{c}" for c in STAT_COLS] + ["prior_win_pct"]]

    def _build_rolling_avg(self, merged: pd.DataFrame, reg_team_games: pd.DataFrame) -> pd.DataFrame:
        """Build each team's postseason-to-date form and blend it with the regular-season baseline."""
        grp_keys = ["team_id", "season"]
        shifted = merged.groupby(grp_keys)[STAT_COLS + ["team_win"]].shift(1)
        games_so_far = merged.groupby(grp_keys).cumcount()

        this_postseason = shifted.groupby([merged["team_id"], merged["season"]]).expanding().mean()
        this_postseason = this_postseason.reset_index(level=[0, 1], drop=True)
        this_postseason.columns = [f"this_postseason_{c}" for c in this_postseason.columns]
        this_postseason = this_postseason.rename(columns={"this_postseason_team_win": "this_postseason_win_pct"})

        merged = pd.concat([merged, this_postseason], axis=1)
        merged = merged.merge(self._build_regular_season_baseline(reg_team_games), on=["team_id", "season"], how="left")

        blend_specs = [(c, f"this_postseason_{c}", f"prior_{c}") for c in STAT_COLS]
        blend_specs.append(("win_pct", "this_postseason_win_pct", "prior_win_pct"))

        for out_col, this_postseason_col, prior_col in blend_specs:
            this_val = merged[this_postseason_col]
            prior_val = merged[prior_col]
            blended = (games_so_far * this_val.fillna(0) + SHRINKAGE_GAMES * prior_val) / (games_so_far + SHRINKAGE_GAMES)
            merged[f"pre_{out_col}"] = blended.where(prior_val.notna(), this_val)

        return merged

    def _add_playoff_history(self, merged: pd.DataFrame, all_playoff_team_games: pd.DataFrame) -> pd.DataFrame:
        """Each team's playoff win rate across all EARLIER postseasons - a secondary,
        low-weight signal on playoff pedigree, kept as its own feature rather than
        blended into the form differentials above (see _build_rolling_avg's docstring)."""
        season_record = (
            all_playoff_team_games.groupby(["team_id", "season"])["team_win"].mean()
            .reset_index().rename(columns={"team_win": "season_playoff_win_pct"})
            .sort_values(["team_id", "season"])
        )
        season_record["playoff_history_win_pct"] = (
            season_record.groupby("team_id")["season_playoff_win_pct"]
            .apply(lambda s: s.shift(1).expanding().mean())
            .reset_index(level=0, drop=True)
        )
        season_record["has_playoff_history"] = season_record["playoff_history_win_pct"].notna().astype(int)
        league_avg = season_record["playoff_history_win_pct"].mean()
        season_record["playoff_history_win_pct"] = season_record["playoff_history_win_pct"].fillna(league_avg)

        return merged.merge(
            season_record[["team_id", "season", "playoff_history_win_pct", "has_playoff_history"]],
            on=["team_id", "season"], how="left",
        )

    def _build_differential(self, merged: pd.DataFrame) -> pd.DataFrame:
        """Convert the per-team features into home-vs-away differentials for modeling."""
        feature_cols = (
            ["days_rest", "b2b", "series_wins_so_far"]
            + [c for c in merged.columns if c.startswith("pre_")]
            + ["playoff_history_win_pct", "has_playoff_history"]
        )
        home_feat = merged[merged.is_home == 1][["game_id", "season", "round", "game_in_series"] + feature_cols + ["team_win"]].copy()
        home_feat.columns = ["game_id", "season", "round", "game_in_series"] + [f"home_{c}" for c in feature_cols] + ["home_win"]

        away_feat = merged[merged.is_home == 0][["game_id"] + feature_cols].copy()
        away_feat.columns = ["game_id"] + [f"away_{c}" for c in feature_cols]

        final_df = home_feat.merge(away_feat, on="game_id", how="inner")

        diff_cols = []
        for c in feature_cols:
            final_df[f"diff_{c}"] = final_df[f"home_{c}"] - final_df[f"away_{c}"]
            diff_cols.append(f"diff_{c}")

        before = len(final_df)
        final_df = final_df.dropna(subset=diff_cols).reset_index(drop=True)
        self.logger.info(f"dropped {before - len(final_df)} playoff rows with no history, {len(final_df)} remain")
        self.logger.info(f"home win rate in playoff modeling set: {final_df['home_win'].mean():.3f}")

        return final_df
