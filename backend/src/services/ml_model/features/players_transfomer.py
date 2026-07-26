import numpy as np
import pandas as pd

from services.ml_model.features.transformer_base import TransformerBase
from config.logger import get_logger

# validated in the exploration notebook: min_games=5 as the noise guard and pts as the
# ranking stat both beat the alternatives (min_games=0, ranking by plus_minus or minutes)
MIN_GAMES = 5
STAR_THRESHOLDS = (5, 10, 20)


class PlayersTransformer(TransformerBase):
    def __init__(self, model_df: pd.DataFrame, df_player_stats: pd.DataFrame, df_games: pd.DataFrame):
        self.model_df = model_df
        self.df_player_stats = df_player_stats
        # copy before converting so we don't mutate the raw df_games the caller still holds
        # a reference to (it's shared with GamesTransformer/BoxscoreTransformer upstream)
        self.df_games = df_games.copy()
        self.df_games["game_date"] = pd.to_datetime(self.df_games["game_date"])
        self.logger = get_logger(__name__)

    def transform(self) -> pd.DataFrame:
        self.logger.info("Transform Apply Player Star...")
        try:
            player_games = self._build_player_games()
            league_ratings = self._build_league_ratings(player_games)
            team_star_counts = self._build_team_star_counts(player_games, league_ratings)
            model_df = self._merge_star_diff(team_star_counts)

            self.logger.info("Transform Apply Player Star Done...")
        except Exception as e:
            self.logger.error(f"Error in transforming player star: {e}")
            raise

        return model_df

    def _build_player_games(self) -> pd.DataFrame:
        player_games = self.df_player_stats[["season_id", "player_id", "team_id", "game_id", "min", "pts"]].merge(
            self.df_games[["game_id", "season_id", "game_date"]], on=["season_id", "game_id"], how="left"
        )
        player_games = player_games.dropna(subset=["game_date"])
        player_games = player_games.sort_values(["player_id", "season_id", "game_date"]).reset_index(drop=True)

        # same leak-free pattern as the team box score: shift(1) before expanding(), per player per season
        player_grp = player_games.groupby(["player_id", "season_id"])
        shifted_pts = player_grp["pts"].shift(1)
        player_games["pre_player_pts"] = (
            shifted_pts.groupby([player_games["player_id"], player_games["season_id"]]).expanding().mean()
            .reset_index(level=[0, 1], drop=True)
        )

        # noise guard: a player with fewer than MIN_GAMES prior games this season has too small a
        # sample to trust as "this is a top scorer" - exclude them from ranking until they clear it
        games_played_prior = player_grp.cumcount()
        player_games.loc[games_played_prior < MIN_GAMES, "pre_player_pts"] = np.nan

        return player_games

    def _build_league_ratings(self, player_games: pd.DataFrame) -> pd.DataFrame:
        # a league-wide "as of this date" rating for every active player, per season, built by
        # carrying each player's most recent known pre_player_pts forward via an as-of join.
        # Ranking only against whoever happened to play that exact night would make "top 20"
        # nearly meaningless on light schedule nights - the comparison pool has to be every
        # active player, always, not just tonight's active roster.
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

        # na_option="keep" (pandas' default) matters here: on a night where every player's history
        # is still empty, na_option="bottom" would tie every one of them for rank 1 instead of
        # correctly excluding them all from the ranking
        league_ratings["league_rank"] = league_ratings.groupby(["season_id", "game_date"])["pre_player_pts"].rank(
            ascending=False, method="min"
        )

        for k in STAR_THRESHOLDS:
            league_ratings[f"is_top{k}"] = (league_ratings["league_rank"] <= k).astype(int)

        return league_ratings

    def _build_team_star_counts(self, player_games: pd.DataFrame, league_ratings: pd.DataFrame) -> pd.DataFrame:
        star_cols = [f"is_top{k}" for k in STAR_THRESHOLDS]

        # which of a team's ACTUAL players that game (known pregame via lineups/injury reports,
        # unlike box-score stats which are only known post-game) are league top5/10/20
        merged = player_games[["season_id", "team_id", "game_id", "player_id", "game_date"]].merge(
            league_ratings[["season_id", "player_id", "game_date"] + star_cols],
            on=["season_id", "player_id", "game_date"], how="left",
        )
        merged[star_cols] = merged[star_cols].fillna(0)

        return merged.groupby(["season_id", "game_id", "team_id"])[star_cols].sum().reset_index()

    def _merge_star_diff(self, team_star_counts: pd.DataFrame) -> pd.DataFrame:
        star_cols = [f"is_top{k}" for k in STAR_THRESHOLDS]

        home_stars = team_star_counts.merge(
            self.df_games[["game_id", "home_team_id"]], left_on=["game_id", "team_id"], right_on=["game_id", "home_team_id"]
        )[["game_id"] + star_cols].rename(columns={f"is_top{k}": f"home_top{k}" for k in STAR_THRESHOLDS})

        away_stars = team_star_counts.merge(
            self.df_games[["game_id", "away_team_id"]], left_on=["game_id", "team_id"], right_on=["game_id", "away_team_id"]
        )[["game_id"] + star_cols].rename(columns={f"is_top{k}": f"away_top{k}" for k in STAR_THRESHOLDS})

        model_df = self.model_df.merge(home_stars, on="game_id", how="left").merge(away_stars, on="game_id", how="left")

        diff_cols = []
        for k in STAR_THRESHOLDS:
            model_df[f"diff_top{k}"] = model_df[f"home_top{k}"] - model_df[f"away_top{k}"]
            diff_cols.append(f"diff_top{k}")

        # drop games where a team's star counts couldn't be computed (e.g. missing player-stat rows)
        before = len(model_df)
        model_df = model_df.dropna(subset=diff_cols).reset_index(drop=True)
        self.logger.info(f"dropped {before - len(model_df)} rows with no star-count coverage, {len(model_df)} remain")

        return model_df
