import pandas as pd
class PlayerStats:
    def __init__(self, player_stats_df: pd.DataFrame, players_info_df: pd.DataFrame, teams_info_df: pd.DataFrame):
        self.player_stats_df = player_stats_df[["season_id", "player_id", "team_id", "pts", "reb", "plus_minus", "ast", "dreb", "oreb", "season"]]
        self.players_info_df = players_info_df[["player_id", "player_name"]]
        self.teams_info_df = teams_info_df[["team_id", "team_name"]]
        self.ALLOWED_STAT_COLS = ["average_points", "average_rebounds", "average_plus_minus", "average_assists", "average_defensive_rebounds", "average_offensive_rebounds"]

    def transform(self) -> pd.DataFrame:
        build_player_games_df = self._build_player_games()
        rank_cols = []
        for stat in self.ALLOWED_STAT_COLS:
            build_player_games_df = self._rank_players(build_player_games_df, stat_col=stat)
            rank_cols.append(f"rank_{stat}")

        # keep a player if they're top 10 in at least one stat, rather than requiring
        # top 10 in every stat (which the old sequential-filter approach effectively did)
        top_10_mask = (build_player_games_df[rank_cols] <= 10).any(axis=1)
        return build_player_games_df.loc[top_10_mask].reset_index(drop=True)


    def _build_player_games(self) -> pd.DataFrame:
        average_stats = self.player_stats_df.groupby(["season_id", "player_id", "team_id", "season"]).agg(
            average_points=pd.NamedAgg(column="pts", aggfunc="mean"),
            average_rebounds=pd.NamedAgg(column="reb", aggfunc="mean"),
            average_plus_minus=pd.NamedAgg(column="plus_minus", aggfunc="mean"),
            average_assists=pd.NamedAgg(column="ast", aggfunc="mean"),
            average_defensive_rebounds=pd.NamedAgg(column="dreb", aggfunc="mean"),
            average_offensive_rebounds=pd.NamedAgg(column="oreb", aggfunc="mean"),
            games_played=pd.NamedAgg(column="player_id", aggfunc="count")
        ).reset_index()

        average_stats = average_stats.merge(self.players_info_df, on=["player_id"], how="left")
        average_stats = average_stats.merge(self.teams_info_df, on=["team_id"], how="left")
        return average_stats.sort_values(["player_name", "season_id"], ascending=[True, False]).reset_index(drop=True)

    def _rank_players(self, df: pd.DataFrame, stat_col: str) -> pd.DataFrame:
        if stat_col not in self.ALLOWED_STAT_COLS:
            raise ValueError(f"Invalid stat_col: {stat_col}. Allowed values are: {self.ALLOWED_STAT_COLS}")
        stat_rank_col = f"rank_{stat_col}"
        df[stat_rank_col] = df.groupby("season_id")[stat_col].rank(ascending=False, method="min")
        return df
