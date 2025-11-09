from logging import getLogger
from app.models import SeasonRecord, TeamInfo, PlayerInfo, TeamRoster, TeamStats, PlayerStats, TeamMatchups
import polars as pl
from sqlalchemy import create_engine
import os
from services.db.models_upsert import TableModelFactory

logger = getLogger(__name__)
class DBService:
    def __init__(self):
        self.table_model_map = {
            "season_record": SeasonRecord,
            "teams_info": TeamInfo,
            "players_info": PlayerInfo,
            "teams_roster": TeamRoster,
            "team_stats": TeamStats,
            "player_stats": PlayerStats,
        }
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.engine = create_engine(f"mysql+pymysql://{self.user}:{self.password}@mysql-host:3307/{self.db_name}")
    
    def upsert_nba_data(self, raw_tables: dict, get_table_name: str = None) -> None:
        logger.info("Starting upsert of NBA data into the database")
        if get_table_name:
            self.table_model_map["team_matchups"] = TeamMatchups
            self.table_model_map = {
                get_table_name: self.table_model_map.get(get_table_name)}
        try:
            for table_name, model in self.table_model_map.items():
                df = raw_tables.get(table_name)
                logger.info(f"Upserting data for table: {table_name}, Number of records: {len(df) if df is not None else 0}")
                if not df.empty:
                    logger.info(f"Upserting data for table: {table_name}")
                    records = df.to_dict(orient="records")
                    for record in records:
                        table_model = TableModelFactory.get_table_model(table_name)
                        table_model.upsert(model, record)
        except Exception as e:
            logger.error(f"Error during upsert operation: {e}")
            raise

    def get_table_data(self, table_name: str) -> dict:
        try:
            query = f"SELECT * FROM {table_name}"
            df = pl.read_database(
                query=query,
                connection=self.engine
            )
            return df.to_dicts()
        except Exception as e:
            logger.error(f"Error retrieving data from table {table_name}: {e}")
            raise
    
    