import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../backend/src"))

from dagster import asset, AssetExecutionContext, Config
from services.data_collection.build_data_service import BuildDataService
from services.object_storage.service import ObjectStorageService
from services.warehouse_storage.bigquery.service import BigQueryService


class SeasonConfig(Config):
    season_year: str
    num_seasons: int

@asset
def raw_nba_data(context: AssetExecutionContext, config: SeasonConfig) -> dict:
    """Collect raw NBA data from the NBA API."""
    season_year = config.season_year
    split_year = season_year.split("-")
    season_id = f"{split_year[0][-2:]}0{split_year[1][-2:]}"

    storage = ObjectStorageService().get_storage()
    raw_tables = {}

    for i in range(config.num_seasons):
        tables = BuildDataService().build_nba_data(season_id=season_id, season_year=season_year)
        context.log.info(f"Collected {len(tables)} tables for season {season_year}")
        for table_name, df in tables.items():
            storage.save(df=df, file_name=table_name, season=season_year)
            context.log.info(f"Saved {table_name} for season {season_year} to GCS")

        raw_tables[season_year] = list(tables.keys())

        # decrement season
        split_year = season_year.split("-")
        # season_year = 2022-23
        season_year = f"{int(split_year[0]) - 1}-{str(int(split_year[1]) - 1)[-2:]}"
        # season_id = 22023
        season_id = f"{str(int(season_id[:2]) - 1)}0{str(int(season_id[2:]) - 1)}"

    return raw_tables


@asset
def bigquery_tables(context: AssetExecutionContext, raw_nba_data: dict) -> None:
    """Load latest GCS parquet files into BigQuery."""
    context.log.info(f"Loading seasons {list(raw_nba_data.keys())} into BigQuery")
    seasons = list(raw_nba_data.keys())
    try:
        BigQueryService().load_latest_data_from_gcs_to_bigquery(seasons=seasons)
    except Exception as e:
        context.log.error(f"Error loading data from GCS to BigQuery: {e}")
        raise e
    context.log.info("Successfully loaded all tables into BigQuery")
