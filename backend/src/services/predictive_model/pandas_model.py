
import pandas as pd

class PandasModel:
    def __init__(self, player_stats_df: pd.DataFrame, team_stats_df: pd.DataFrame, team_matchups_df: pd.DataFrame): 
        self.player_stats_df = player_stats_df
        self.team_stats_df = team_stats_df
        self.team_matchups_df = team_matchups_df
    
    def _prepare_data(self):
        pass


