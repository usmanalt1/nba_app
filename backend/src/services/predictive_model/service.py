from services.db.db_service import DBService
from services.predictive_model.constants import Constants
from services.predictive_model.model import Model
import polars as pl

class PredictiveModelService(Constants):
    def __init__(self):
        self.db_service = DBService()
        self.tables_to_fetch = [self.PLAYER_STATS_TABLE, self.TEAM_MATCHUPS_TABLE, self.TEAM_STATS_TABLE]  

    def run(self):
        df_tables = self._get_tables() 
        model = Model(
            player_stats_df=df_tables[self.PLAYER_STATS_TABLE],
            team_stats_df=df_tables[self.TEAM_STATS_TABLE],
            team_matchups_df=df_tables[self.TEAM_MATCHUPS_TABLE]
        )
        merged_teams_player_stats_df, team_matchups_df = model.run()
        return merged_teams_player_stats_df, team_matchups_df
    
    def _get_tables(self):
        df_tables = {}
        for table in self.tables_to_fetch:
            table_dict = self.db_service.get_table_data(table_name=table)
            pl_df = pl.DataFrame(table_dict)
            df_tables[table] = pl_df
        return df_tables