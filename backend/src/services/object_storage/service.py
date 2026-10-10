import os
import pandas as pd
import gcsfs
from config.settings import settings
from services.interface import StorageBase
from google.cloud import storage
import pandas as pd
from azure.core.exceptions import AzureError


from logging import getLogger
logger = getLogger(__name__)

class ObjectStorageService:
    
    def __init__(self, generate_run_id=None):
        self.generate_run_id = generate_run_id or pd.Timestamp.now().strftime("%Y%m%d%H%M%S")

    def get_storage(self) -> "StorageBase":
        if settings.STORAGE == "gcs":
            return GCSStorage(generate_run_id=self.generate_run_id)
        elif settings.STORAGE == "az":
            logger.info("Saving to Azure Blob...")
            return AzureBlobStorage(file_format=settings.FILE_FORMAT, run_id=self.generate_run_id)
        else:
            return LocalStorage(generate_run_id=self.generate_run_id)

class GCSStorage(StorageBase):
    def __init__(self, generate_run_id=None):
        self.settings = settings
        self.file_format = self.settings.FILE_FORMAT
        self.bucket = self.settings.PARENT_BUCKET
        self.generate_run_id = generate_run_id
        self.fs = gcsfs.GCSFileSystem(
            project=self.settings.GCS_PROJECT_NAME,
            token=self.settings.GCS_SERVICE_ACCOUNT_JSON,
        )
        self.storage_client = storage.Client.from_service_account_json(
            self.settings.GCS_SERVICE_ACCOUNT_JSON,
            project=self.settings.GCS_PROJECT_NAME
        )

    def save(self, df: pd.DataFrame, file_name: str, season: str) -> None:
        path = f"gs://{self.bucket}/{self.generate_run_id}/season={season}/{file_name}.{self.file_format}"
        try:
            with self.fs.open(path, "wb") as f:
                df.to_parquet(f, index=False)
            logger.info(f"Saved to GCS: {path}")
        except Exception:
            logger.exception(f"Failed to write parquet to GCS: {path}")
            raise
    
    def read(self, latest_run_id: str, seasons: list, table: str) -> pd.DataFrame:
        dfs = []
        run_timestamp = pd.Timestamp.now()
        for season in seasons:
            path = f"{self.bucket}/{latest_run_id}/season={season}/{table}.{self.file_format}"
            try:
                with self.fs.open(path, "rb") as f:
                    df = pd.read_parquet(f)
                    df["season"] = season
                    df["run_timestamp"] = run_timestamp
                    dfs.append(df)
            except FileNotFoundError:
                logger.warning(f"No data for season={season}, table={table}")
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    def read_run(self, run_id: str = None) -> dict:
        """Every table written under a run, keyed by table name, seasons concatenated."""
        # The collecting asset wrote this run in-process, so a stale listing would miss it.
        self.fs.invalidate_cache()

        run_id = run_id or self._latest_run_id()
        if run_id is None:
            logger.warning(f"No run_id prefixes found in gs://{self.bucket}")
            return {}

        seasons, tables = self._list_run(run_id)
        if not tables:
            raise FileNotFoundError(f"Run {run_id} has no {self.file_format} files in gs://{self.bucket}")
        logger.info(f"Reading run {run_id} from gs://{self.bucket}: {len(tables)} tables, seasons {seasons}")

        run = {}
        for table in tables:
            df = self.read(latest_run_id=run_id, seasons=seasons, table=table)
            if not df.empty:
                run[table] = df
        return run

    def _latest_run_id(self) -> str:
        run_ids = [path.rstrip("/").rsplit("/", 1)[-1] for path in self.fs.ls(self.bucket)]
        run_ids = [run_id for run_id in run_ids if run_id]
        return max(run_ids) if run_ids else None

    def _list_run(self, run_id: str) -> tuple:
        """The (seasons, tables) present under one run."""
        paths = self.fs.glob(f"{self.bucket}/{run_id}/season=*/*.{self.file_format}")
        seasons, tables = set(), set()
        for path in paths:
            season_dir, file_name = path.rsplit("/", 2)[-2:]
            seasons.add(season_dir.split("=", 1)[1])
            tables.add(file_name.rsplit(".", 1)[0])
        return sorted(seasons), sorted(tables)


class AzureBlobStorage(StorageBase):
    def __init__(self, file_format: str, run_id: str):
        self.settings = settings
        self.container_name = self.settings.CONTAINER_NAME
        self.file_format = file_format
        self.latest_run_id = run_id

    def save(self, df: pd.DataFrame, file_name: str, season: str) -> None:
        blob_name = f"nba_raw/{self.latest_run_id}/season={season}/{file_name}.{self.file_format}"
        logger.info(f"Saving file to {blob_name} in {self.container_name}...")
        path = f"az://{self.container_name}/{blob_name}"
        storage_options = {"connection_string": self.settings.CONN_STR}
        try:
            df.to_parquet(path, index=False, storage_options=storage_options)
            logger.info(f"Saved file in blob: {path}")
        except Exception:
            logger.exception(f"Failed to write parquet to Azure Blob: {path}")
            raise

    def read(self, latest_run_id: str, seasons: list, table: str) -> pd.DataFrame:
        pass

class LocalStorage(StorageBase):
    def __init__(self, generate_run_id=None):
        self.settings = settings
        self.file_format = self.settings.FILE_FORMAT
        self.parent_dir = self.settings.PARENT_BUCKET
        self.generate_run_id = generate_run_id
        self.path = f"{self.parent_dir}/{self.generate_run_id}"

    def save(self, df: pd.DataFrame, file_name: str, season: str) -> None:
        file_path = f"{self.path}/season={season}"
        try:
            os.makedirs(file_path, exist_ok=True)
        except Exception:
            logger.exception(f"Failed to create directory: {file_path}")
            raise

        full_path = f"{file_path}/{file_name}.{self.file_format}"
        df["season"] = season
        try:
            df.to_parquet(full_path, index=False, engine="fastparquet")
        except Exception:
            logger.warning("fastparquet write failed, trying pyarrow engine")
            try:
                df.to_parquet(full_path, index=False, engine="pyarrow")
            except Exception:
                logger.exception(f"Failed to write parquet file: {full_path}")
                raise

        logger.info(f"Saved to local storage: {full_path}")
    
    def read(self, latest_run_id: str, seasons: list, table: str) -> pd.DataFrame:
        dfs = []
        run_timestamp = pd.Timestamp.now()
        for season in seasons:
            file_path = f"{self.parent_dir}/{latest_run_id}/season={season}/{table}.{self.file_format}"
            if os.path.exists(file_path):
                try:
                    df = pd.read_parquet(file_path)
                    df["season"] = season
                    df["run_timestamp"] = run_timestamp
                    dfs.append(df)
                except Exception:
                    logger.exception(f"Failed to read parquet file: {file_path}")
            else:
                logger.warning(f"No data for season={season}, table={table} at path: {file_path}")
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
