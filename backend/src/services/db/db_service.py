from logging import getLogger
from pathlib import Path
from app.models import SeasonRecord, TeamInfo, PlayerInfo, TeamRoster, TeamStats, PlayerStats, TeamMatchups, PlayerAwards, DimGames, FctTeamStats, FctPlayerStats
from sqlalchemy import create_engine
import os
from services.db.models_upsert import TableModelFactory
from services.interface import StorageBase
import pandas as pd
from config.settings import settings

logger = getLogger(__name__)

class DBService(StorageBase):
    def __init__(self):
        self.table_model_map = {
            "season_record": SeasonRecord,
            "teams_info": TeamInfo,
            "players_info": PlayerInfo,
            "teams_roster": TeamRoster,
            "team_stats": TeamStats,
            "player_stats": PlayerStats,
            "team_matchups": TeamMatchups,
            "player_awards": PlayerAwards,
            "dim_games": DimGames,
            "fct_team_stats": FctTeamStats,
            "fct_player_stats": FctPlayerStats
        }
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.postgres_host = os.getenv("DB_HOST")
        self.engine = create_engine(f"postgresql://{self.user}:{self.password}@{self.postgres_host}:5432/{self.db_name}")
        self.file_path_parent_name = os.getenv("FILE_PATH_PARENT_NAME")

    def _get_latest_files_using_path(self) -> dict:
        # If path is nba_data/run_id/season=season_id/table_name.parquet, we want to get the latest run_id and read all files for that run_id
        parent_path = Path(self.file_path_parent_name)
        if not parent_path.exists():
            logger.warning(f"Parent path {self.file_path_parent_name} does not exist. No data loaded into DuckDB.")
            return {}
        run_ids = [d.name for d in parent_path.iterdir() if d.is_dir()]
        if not run_ids:
            logger.warning(f"No run_id directories found in {self.file_path_parent_name}. No data loaded into DuckDB.")
            return {}
        latest_run_id = max(run_ids)
        logger.info(f"Latest run_id found: {latest_run_id}")
        latest_run_path = parent_path / latest_run_id
        table_dict = {}
        for season_dir in latest_run_path.iterdir():
            if season_dir.is_dir() and season_dir.name.startswith("season="):
                for file in season_dir.iterdir():
                    if file.is_file() and file.suffix == f".{settings.FILE_FORMAT}":
                        table_name = file.stem
                        try:
                            prev_df = table_dict.get(table_name, pd.DataFrame())
                            df = pd.read_parquet(file)
                            if prev_df.empty:
                                table_dict[table_name] = df
                            else:
                                all_df = pd.concat([prev_df, df], ignore_index=True)
                                table_dict[table_name] = all_df
                            logger.info(f"Loaded file {file} into DataFrame for table {table_name}")
                        except Exception:
                            logger.exception(f"Failed to read parquet file: {file}")
        return table_dict
    
    def save(self) -> None:
        logger.info("Starting upsert of NBA data into the database")
        dfs = self._get_latest_files_using_path()
        try:
            for table_name, model in self.table_model_map.items():
                df: dict = dfs.get(table_name)
                logger.info(f"Upserting data for table: {table_name}, Number of records: {len(df) if df is not None else 0}")
                # not every run produces every table (e.g. player_awards is only present
                # in runs that hit /collect/player_awards) - df is None when this table
                # simply wasn't part of the latest run, not an error.
                if df is not None and not df.empty:
                    logger.info(f"Upserting data for table: {table_name}")
                    # convert pandas NaN -> None so optional/sparse fields store as real SQL
                    # NULL instead of the literal string "nan"
                    df = df.where(pd.notnull(df), None)
                    records = df.to_dict(orient="records")
                    table_model = TableModelFactory.get_table_model(table_name)
                    table_model.upsert_many(model, records)
        except Exception as e:
            logger.error(f"Error during upsert operation: {e}")
            raise
    
    def read(self, table_name: str, df: bool = True):
        model = self.table_model_map[table_name]
        table_model = TableModelFactory.get_table_model(table_name)
        model_list = table_model.read(model)

        if df:
            return pd.DataFrame(model_list)

        return model_list