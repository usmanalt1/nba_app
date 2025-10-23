
from services.data_collection.collect import CollectRawNBAData
from datetime import datetime, timedelta

class BuildDataService:
    def __init__(self, date = None):
        self.date = date or datetime.today() - timedelta(weeks=52)

    def build_nba_data(self, table_name = None):
        raw_tables = CollectRawNBAData(date_to_run=self.date).gather_and_import_nba_data(table_name=table_name)

        return raw_tables