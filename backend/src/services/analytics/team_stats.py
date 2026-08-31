import pandas as pd


class TeamStats:
    def __init__(self, team_stats_df: pd.DataFrame, teams_info_df: pd.DataFrame):
        self.team_stats_df = team_stats_df[["season_id", "team_id", "pts", "reb", "plus_minus", "ast", "season", "wl"]]
        self.teams_info_df = teams_info_df[["team_id", "team_name"]]
        self.ALLOWED_STAT_COLS = ["average_points", "average_rebounds", "average_plus_minus", "average_assists"]

    def transform(self) -> pd.DataFrame:
        build_team_games_df = self._build_team_games()
        rank_cols = []
        for stat in self.ALLOWED_STAT_COLS:
            build_team_games_df = self._rank_teams(build_team_games_df, stat_col=stat)
            rank_cols.append(f"rank_{stat}")

        top_10_mask = (build_team_games_df[rank_cols] <= 10).any(axis=1)
        return build_team_games_df.loc[top_10_mask].reset_index(drop=True)

    def _build_team_games(self) -> pd.DataFrame:
        df = self.team_stats_df.copy()
        df["win"] = (df["wl"] == "W").astype(int)

        average_stats = df.groupby(["season_id", "team_id", "season"]).agg(
            average_points=pd.NamedAgg(column="pts", aggfunc="mean"),
            average_rebounds=pd.NamedAgg(column="reb", aggfunc="mean"),
            average_plus_minus=pd.NamedAgg(column="plus_minus", aggfunc="mean"),
            average_assists=pd.NamedAgg(column="ast", aggfunc="mean"),
            wins=pd.NamedAgg(column="win", aggfunc="sum"),
            games_played=pd.NamedAgg(column="win", aggfunc="count"),
        ).reset_index()

        average_stats["win_pct"] = average_stats["wins"] / average_stats["games_played"]
        average_stats = average_stats.merge(self.teams_info_df, on=["team_id"], how="left")
        return average_stats.sort_values(["team_name", "season_id"], ascending=[True, False]).reset_index(drop=True)

    def _rank_teams(self, df: pd.DataFrame, stat_col: str) -> pd.DataFrame:
        if stat_col not in self.ALLOWED_STAT_COLS:
            raise ValueError(f"Invalid stat_col: {stat_col}. Allowed values are: {self.ALLOWED_STAT_COLS}")
        stat_rank_col = f"rank_{stat_col}"
        df[stat_rank_col] = df.groupby("season_id")[stat_col].rank(ascending=False, method="min")
        return df
