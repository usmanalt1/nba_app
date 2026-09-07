"""Create player-form features used to model team star quality."""

import numpy as np
import pandas as pd

from services.ml_model.features.transformer_base import TransformerBase
from config.logger import get_logger

MIN_GAMES = 5
STAR_THRESHOLDS = (5, 10, 20)
STAR_SHRINKAGE_GAMES = 10


class PlayersTransformer(TransformerBase):
    """Build player star features and merge them into the model dataset."""

    def __init__(self, model_df: pd.DataFrame, df_player_stats: pd.DataFrame, df_games: pd.DataFrame):
        self.model_df = model_df
        self.df_player_stats = df_player_stats
        self.df_games = df_games.copy()
        self.df_games["game_date"] = pd.to_datetime(self.df_games["game_date"])
        self.df_games["season_id"] = self.df_games["season_id"].astype(str)
        self.logger = get_logger(__name__)

    def transform(self) -> pd.DataFrame:
        self.logger.info("Transform Apply Player Star...")
        try:
            player_games = self._build_player_games()
            league_ratings = self._build_league_ratings(player_games)
            team_star_counts = self._build_team_star_counts(player_games, league_ratings)
            team_star_baseline = self._build_team_star_baseline(team_star_counts)
            model_df = self._merge_star_diff(team_star_counts, team_star_baseline)

            self.logger.info("Transform Apply Player Star Done...")
        except Exception as e:
            self.logger.error(f"Error in transforming player star: {e}")
            raise

        return model_df

    def _build_player_games(self) -> pd.DataFrame:
        """Join player stats to game dates and build the prior-game scoring feature."""
        player_stats = self.df_player_stats[["season_id", "player_id", "team_id", "game_id", "min", "pts"]].copy()
        player_stats["season_id"] = player_stats["season_id"].astype(str)

        player_games = player_stats.merge(
            self.df_games[["game_id", "season_id", "game_date"]], on=["season_id", "game_id"], how="left"
        )
        player_games = player_games.dropna(subset=["game_date"])
        player_games = player_games.sort_values(["player_id", "season_id", "game_date"]).reset_index(drop=True)

        player_grp = player_games.groupby(["player_id", "season_id"])
        shifted_pts = player_grp["pts"].shift(1)
        player_games["pre_player_pts"] = (
            shifted_pts.groupby([player_games["player_id"], player_games["season_id"]]).expanding().mean()
            .reset_index(level=[0, 1], drop=True)
        )

        games_played_prior = player_grp.cumcount()
        player_games.loc[games_played_prior < MIN_GAMES, "pre_player_pts"] = np.nan

        return player_games

    def _build_league_ratings(self, player_games: pd.DataFrame) -> pd.DataFrame:
        """Build season-by-season player ratings from the latest known prior-game form."""
        events = player_games.dropna(subset=["pre_player_pts"])[
            ["season_id", "player_id", "game_date", "pre_player_pts"]
        ].sort_values("game_date")

        all_dates = self.df_games[["season_id", "game_date"]].drop_duplicates().sort_values("game_date")

        rating_frames = []
        for season_id, season_events in events.groupby("season_id"):
            season_dates = all_dates.loc[all_dates["season_id"] == season_id, "game_date"]
            players = season_events["player_id"].unique()

            query = pd.MultiIndex.from_product(
                [players, season_dates], names=["player_id", "game_date"]
            ).to_frame(index=False).sort_values("game_date")

            asof = pd.merge_asof(
                query,
                season_events.sort_values("game_date")[["player_id", "game_date", "pre_player_pts"]],
                on="game_date", by="player_id", direction="backward",
            )
            asof["season_id"] = season_id
            rating_frames.append(asof)

        league_ratings = pd.concat(rating_frames, ignore_index=True).dropna(subset=["pre_player_pts"])
        league_ratings["season_id"] = league_ratings["season_id"].astype(str)

        league_ratings["league_rank"] = league_ratings.groupby(["season_id", "game_date"])["pre_player_pts"].rank(
            ascending=False, method="min"
        )

        for k in STAR_THRESHOLDS:
            league_ratings[f"is_top{k}"] = (league_ratings["league_rank"] <= k).astype(int)

        return league_ratings

    def _build_team_star_counts(self, player_games: pd.DataFrame, league_ratings: pd.DataFrame) -> pd.DataFrame:
        """Count how many players on each team met the league star thresholds for a game."""
        star_cols = [f"is_top{k}" for k in STAR_THRESHOLDS]

        merged = player_games[["season_id", "team_id", "game_id", "player_id", "game_date"]].merge(
            league_ratings[["season_id", "player_id", "game_date"] + star_cols],
            on=["season_id", "player_id", "game_date"], how="left",
        )
        merged[star_cols] = merged[star_cols].fillna(0)

        return merged.groupby(["season_id", "game_id", "team_id"])[star_cols].sum().reset_index()

    def _build_prior_season_star_baseline(self, counts: pd.DataFrame, star_cols: list) -> pd.DataFrame:
        """Use the previous season's average star count as a fallback baseline."""
        prior_cols = [f"prior_{c}" for c in star_cols]
        season_avg = (
            counts.groupby(["team_id", "season_id"])[star_cols].mean().reset_index()
            .rename(columns={c: f"prior_{c}" for c in star_cols})
            .sort_values(["team_id", "season_id"])
        )
        season_avg[prior_cols] = season_avg.groupby("team_id")[prior_cols].shift(1)

        return season_avg[["team_id", "season_id"] + prior_cols]

    def _build_team_schedule(self) -> pd.DataFrame:
        """Create one row per team per game, including scheduled games with no played stats yet."""
        home = self.df_games[["game_id", "season_id", "game_date", "home_team_id"]].rename(columns={"home_team_id": "team_id"})
        away = self.df_games[["game_id", "season_id", "game_date", "away_team_id"]].rename(columns={"away_team_id": "team_id"})
        return pd.concat([home, away], ignore_index=True)

    def _build_team_star_baseline(self, team_star_counts: pd.DataFrame) -> pd.DataFrame:
        """Create a rolling team star baseline and blend it with last season's average."""
        star_cols = [f"is_top{k}" for k in STAR_THRESHOLDS]
        grp_keys = ["team_id", "season_id"]

        team_schedule_with_stars = self._build_team_schedule().merge(
            team_star_counts, on=["team_id", "season_id", "game_id"], how="left"
        )
        team_schedule_with_stars = team_schedule_with_stars.sort_values(grp_keys + ["game_date"])

        prior_game_star_counts = team_schedule_with_stars.groupby(grp_keys)[star_cols].shift(1)
        games_so_far = team_schedule_with_stars.groupby(grp_keys).cumcount()

        season_to_date_star_avg = prior_game_star_counts.groupby([
            team_schedule_with_stars["team_id"], team_schedule_with_stars["season_id"]
        ]).expanding().mean()
        season_to_date_star_avg = season_to_date_star_avg.reset_index(level=[0, 1], drop=True)
        season_to_date_star_avg.columns = [f"this_season_{c}" for c in season_to_date_star_avg.columns]

        team_schedule_with_stars = pd.concat([team_schedule_with_stars, season_to_date_star_avg], axis=1)
        team_schedule_with_stars = team_schedule_with_stars.merge(
            self._build_prior_season_star_baseline(team_schedule_with_stars, star_cols),
            on=grp_keys,
            how="left",
        )

        for k in STAR_THRESHOLDS:
            col = f"is_top{k}"
            this_season_val = team_schedule_with_stars[f"this_season_{col}"]
            prior_season_val = team_schedule_with_stars[f"prior_{col}"]
            blended = (
                games_so_far * this_season_val.fillna(0)
                + STAR_SHRINKAGE_GAMES * prior_season_val
            ) / (games_so_far + STAR_SHRINKAGE_GAMES)
            team_schedule_with_stars[f"pre_top{k}"] = blended.where(prior_season_val.notna(), this_season_val)

        return team_schedule_with_stars[["team_id", "season_id", "game_id"] + [f"pre_top{k}" for k in STAR_THRESHOLDS]]

    def _merge_star_diff(self, team_star_counts: pd.DataFrame, team_star_baseline: pd.DataFrame) -> pd.DataFrame:
        """Merge home/away star counts into the base model and compute star differentials."""
        star_cols = [f"is_top{k}" for k in STAR_THRESHOLDS]
        baseline_cols = [f"pre_top{k}" for k in STAR_THRESHOLDS]

        home_stars = team_star_counts.merge(
            self.df_games[["game_id", "home_team_id"]],
            left_on=["game_id", "team_id"],
            right_on=["game_id", "home_team_id"],
        )[["game_id"] + star_cols].rename(columns={f"is_top{k}": f"home_top{k}" for k in STAR_THRESHOLDS})

        away_stars = team_star_counts.merge(
            self.df_games[["game_id", "away_team_id"]],
            left_on=["game_id", "team_id"],
            right_on=["game_id", "away_team_id"],
        )[["game_id"] + star_cols].rename(columns={f"is_top{k}": f"away_top{k}" for k in STAR_THRESHOLDS})

        home_baseline = team_star_baseline.merge(
            self.df_games[["game_id", "home_team_id"]],
            left_on=["game_id", "team_id"],
            right_on=["game_id", "home_team_id"],
        )[["game_id"] + baseline_cols].rename(columns={f"pre_top{k}": f"home_pre_top{k}" for k in STAR_THRESHOLDS})

        away_baseline = team_star_baseline.merge(
            self.df_games[["game_id", "away_team_id"]],
            left_on=["game_id", "team_id"],
            right_on=["game_id", "away_team_id"],
        )[["game_id"] + baseline_cols].rename(columns={f"pre_top{k}": f"away_pre_top{k}" for k in STAR_THRESHOLDS})

        model_df = (
            self.model_df
            .merge(home_stars, on="game_id", how="left")
            .merge(away_stars, on="game_id", how="left")
            .merge(home_baseline, on="game_id", how="left")
            .merge(away_baseline, on="game_id", how="left")
        )

        diff_cols = []
        for k in STAR_THRESHOLDS:
            home_top = model_df[f"home_top{k}"].fillna(model_df[f"home_pre_top{k}"])
            away_top = model_df[f"away_top{k}"].fillna(model_df[f"away_pre_top{k}"])
            model_df[f"home_top{k}"] = home_top
            model_df[f"away_top{k}"] = away_top
            model_df[f"diff_top{k}"] = home_top - away_top
            diff_cols.append(f"diff_top{k}")

        model_df = model_df.drop(columns=[f"{side}_pre_top{k}" for side in ("home", "away") for k in STAR_THRESHOLDS])

        before = len(model_df)
        model_df = model_df.dropna(subset=diff_cols).reset_index(drop=True)
        self.logger.info(f"dropped {before - len(model_df)} rows with no star-count coverage, {len(model_df)} remain")

        return model_df
