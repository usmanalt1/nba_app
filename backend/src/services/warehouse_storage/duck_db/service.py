
import duckdb
import pandas as pd
import os
from config.settings import settings
from pathlib import Path


from logging import getLogger
logger = getLogger(__name__)

class DuckDBService:
    def __init__(self, file_path_parent_name: str = "nba-ua-dev-bucket", db_path: str = "nba_dataset.duckdb"):
        self.db_path = db_path
        self.file_path_parent_name = file_path_parent_name
        self._create_duckdb_database(db_path=self.db_path)
        
        self.table_dict = self._get_latest_files_using_path()
        self._load_dataframes_to_duckdb(dfs=self.table_dict)

    def _create_duckdb_database(self, db_path: str = "nba_dataset.duckdb") -> None:
        logger.info(f"Creating DuckDB database at {db_path}...")
        con = duckdb.connect(db_path)
        con.close()
        logger.info(f"DuckDB database created at {db_path}")
        return None

    def _load_dataframes_to_duckdb(self, dfs: dict, db_path: str = "nba_dataset.duckdb") -> None:
        # This method takes a dictionary of DataFrames and loads them into the DuckDB database. The keys of the dictionary are used as table names.
        logger.info(f"Loading DataFrames into DuckDB database at {db_path}...")
        con = duckdb.connect(db_path)
        # create schema if not exists
        con.execute("CREATE SCHEMA IF NOT EXISTS test")
        for table_name, df in dfs.items():
            con.execute(f"CREATE OR REPLACE TABLE test.{table_name} AS SELECT * FROM df")
            logger.info(f"DataFrame loaded into DuckDB table: test.{table_name}")

            logger.info(f"Verifying data load for table test.{table_name} by fetching row count...")
            row_count = con.execute(f"SELECT COUNT(*) FROM test.{table_name}").fetchone()[0]
            logger.info(f"Row count for table test.{table_name}: {row_count}")

            # Show tables
            tables = con.execute("SHOW TABLES").fetchall()
            logger.info(f"Current tables in DuckDB database: {[table[0] for table in tables]}")

            # Show schemas in db
            schemas = con.execute("SELECT DISTINCT table_schema FROM information_schema.tables").fetchall()
            logger.info(f"Current schemas in DuckDB database: {[schema[0] for schema in schemas]}")

        con.close()
        logger.info(f"All DataFrames loaded into DuckDB database: {db_path}")
        return None
    
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
                            df = pd.read_parquet(file)
                            table_dict[table_name] = df
                            logger.info(f"Loaded file {file} into DataFrame for table {table_name}")
                        except Exception:
                            logger.exception(f"Failed to read parquet file: {file}")
        return table_dict
