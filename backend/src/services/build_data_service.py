
from services.data_collection.collect import CollectRawNBAData
from datetime import datetime, timedelta

class BuildDataService:
    def __init__(self, date = None):
        self.date = date or datetime.today() - timedelta(weeks=52)

    def build_nba_data(self, table_name = None, season_id: str = None, season_year: str = None) -> dict:
        raw_tables = CollectRawNBAData(date_to_run=self.date).gather_and_import_nba_data(table_name=table_name, season_id=season_id, season_year=season_year)

        return raw_tables