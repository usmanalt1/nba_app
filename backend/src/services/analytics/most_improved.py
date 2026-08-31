import pandas as pd

MIN_GAMES = 20

# season_id "2xxxx" is regular season, "4xxxx" is playoffs for the same year - mixing them
# would compare a full 82-game season against a handful of playoff games, so year-over-year
# improvement is always computed on regular season only.
def _regular_season_only(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["season_id"].astype(str).str.startswith("4")]


class MostImprovedPlayers:
    def __init__(self, player_stats_df: pd.DataFrame, players_info_df: pd.DataFrame, teams_info_df: pd.DataFrame):
        self.player_stats_df = _regular_season_only(player_stats_df)[["season_id", "player_id", "team_id", "pts", "season"]]
        self.players_info_df = players_info_df[["player_id", "player_name"]]
        self.teams_info_df = teams_info_df[["team_id", "team_name"]]

    def transform(self) -> pd.DataFrame:
        season_stats = self._build_season_stats()

        seasons = sorted(season_stats["season_id"].unique())
        if len(seasons) < 2:
            return season_stats.iloc[0:0]

        current_season, previous_season = seasons[-1], seasons[-2]
        current = season_stats[season_stats["season_id"] == current_season]
        previous = season_stats[season_stats["season_id"] == previous_season]

        merged = current.merge(
            previous[["player_id", "average_points", "games_played"]],
            on="player_id",
            suffixes=("", "_previous"),
        )
        merged = merged[
            (merged["games_played"] >= MIN_GAMES) & (merged["games_played_previous"] >= MIN_GAMES)
        ]
        merged["points_improvement"] = merged["average_points"] - merged["average_points_previous"]
        merged = merged.rename(columns={
            "average_points": "current_average_points",
            "average_points_previous": "previous_average_points",
        })
        return merged.sort_values("points_improvement", ascending=False).head(10).reset_index(drop=True)

    def _build_season_stats(self) -> pd.DataFrame:
        stats = self.player_stats_df.groupby(["season_id", "player_id", "team_id", "season"]).agg(
            average_points=pd.NamedAgg(column="pts", aggfunc="mean"),
            games_played=pd.NamedAgg(column="pts", aggfunc="count"),
        ).reset_index()
        stats = stats.merge(self.players_info_df, on="player_id", how="left")
        stats = stats.merge(self.teams_info_df, on="team_id", how="left")
        return stats


class MostImprovedTeams:
    def __init__(self, team_stats_df: pd.DataFrame, teams_info_df: pd.DataFrame):
        self.team_stats_df = _regular_season_only(team_stats_df)[["season_id", "team_id", "season", "wl"]]
        self.teams_info_df = teams_info_df[["team_id", "team_name"]]

    def transform(self) -> pd.DataFrame:
        season_stats = self._build_season_stats()

        seasons = sorted(season_stats["season_id"].unique())
        if len(seasons) < 2:
            return season_stats.iloc[0:0]

        current_season, previous_season = seasons[-1], seasons[-2]
        current = season_stats[season_stats["season_id"] == current_season]
        previous = season_stats[season_stats["season_id"] == previous_season]

        merged = current.merge(
            previous[["team_id", "win_pct", "games_played"]],
            on="team_id",
            suffixes=("", "_previous"),
        )
        merged = merged[
            (merged["games_played"] >= MIN_GAMES) & (merged["games_played_previous"] >= MIN_GAMES)
        ]
        merged["win_pct_improvement"] = merged["win_pct"] - merged["win_pct_previous"]
        merged = merged.rename(columns={
            "win_pct": "current_win_pct",
            "win_pct_previous": "previous_win_pct",
        })
        return merged.sort_values("win_pct_improvement", ascending=False).head(10).reset_index(drop=True)

    def _build_season_stats(self) -> pd.DataFrame:
        df = self.team_stats_df.copy()
        df["win"] = (df["wl"] == "W").astype(int)
        stats = df.groupby(["season_id", "team_id", "season"]).agg(
            wins=pd.NamedAgg(column="win", aggfunc="sum"),
            games_played=pd.NamedAgg(column="win", aggfunc="count"),
        ).reset_index()
        stats["win_pct"] = stats["wins"] / stats["games_played"]
        stats = stats.merge(self.teams_info_df, on="team_id", how="left")
        return stats
