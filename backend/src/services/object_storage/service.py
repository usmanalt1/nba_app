import os
import pandas as pd
import gcsfs
from config.settings import settings
from logging import getLogger
logger = getLogger(__name__)
from abc import ABC, abstractmethod

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

    def save(self, df: pd.DataFrame, file_name: str, season: str) -> None:
        path = f"gs://{self.bucket}/{self.generate_run_id}/season={season}/{file_name}.{self.file_format}"
        try:
            with self.fs.open(path, "wb") as f:
                df.to_parquet(f, index=False)
            logger.info(f"Saved to GCS: {path}")
        except Exception:
            logger.exception(f"Failed to write parquet to GCS: {path}")
            raise

    def read_from_object_storage(self, file_path: str, file_name: str) -> pd.DataFrame:
        path = f"gs://{self.bucket}/{file_path}/{file_name}.{self.file_format}"
        try:
            with self.fs.open(path, "rb") as f:
                return pd.read_parquet(f)
        except Exception:
            logger.exception(f"Failed to read parquet from GCS: {path}")
            raise

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

    def read_from_object_storage(self, file_path: str, file_name: str) -> pd.DataFrame:
        full_path = f"{file_path}/{file_name}.{self.file_format}"
        try:
            return pd.read_parquet(full_path, engine="fastparquet")
        except Exception:
            logger.warning("fastparquet read failed, trying pyarrow engine")
            return pd.read_parquet(full_path, engine="pyarrow")
