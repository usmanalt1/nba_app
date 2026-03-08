import os
import pandas as pd
import gcsfs
from config.settings import settings
from abc import ABC, abstractmethod
from google.cloud import storage
import pyarrow.dataset as ds

from logging import getLogger
logger = getLogger(__name__)

class ObjectStorageService:
    def __init__(self):
        self.generate_run_id = pd.Timestamp.now().strftime("%Y%m%d%H%M%S")
        self.factory = {
            "local": LocalStorage(generate_run_id=self.generate_run_id),
            "gcs": GCSStorage(generate_run_id=self.generate_run_id),
        }

    def get_storage(self) -> "ObjectStorageBase":
        return self.factory[settings.STORAGE]

class ObjectStorageBase(ABC):
    @abstractmethod
    def save(self, df: pd.DataFrame, file_name: str, season: str) -> None:
        pass

    @abstractmethod
    def read(self, latest_run_id: str, seasons: list, table: str) -> pd.DataFrame:
        pass

class GCSStorage(ObjectStorageBase):
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
        for season in seasons:
            path = f"{self.bucket}/{latest_run_id}/season={season}/{table}.{self.file_format}"
            try:
                with self.fs.open(path, "rb") as f:
                    df = pd.read_parquet(f)
                    df["season"] = season
                    dfs.append(df)
            except FileNotFoundError:
                logger.warning(f"No data for season={season}, table={table}")
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

class LocalStorage(ObjectStorageBase):
    def __init__(self, generate_run_id=None):
        self.settings = settings
        self.file_format = self.settings.FILE_FORMAT
        self.parent_dir = self.settings.PARENT_BUCKET
        self.generate_run_id = generate_run_id

    def save(self, df: pd.DataFrame, file_name: str, season: str) -> None:
        # ensure target directory exists
        file_path = f"{self.parent_dir}/{self.generate_run_id}/season={season}"
        try:
            os.makedirs(file_path, exist_ok=True)
        except Exception:
            logger.exception(f"Failed to create directory: {file_path}")
            raise

        full_path = f"{file_path}/{file_name}.{self.file_format}"
        # attempt to write with fastparquet first, fall back to pyarrow
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
    
    def read(self, latest_run_id: str, seasons: list) -> pd.DataFrame:
        pass
