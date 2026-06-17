from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DJANGO_SECRET_KEY: str = "changeme"
    DEBUG: bool = False
    ENVIRONMENT: str = "local"
    STORAGE: str = "local"
    PARENT_BUCKET: str = "nba_data"
    FILE_FORMAT: str = "parquet"
    GCS_PROJECT_NAME: str = "NBAPredction"
    GCS_SERVICE_ACCOUNT_JSON: str = "nbapreduction_service_account.json"
    BIGQUERY_DATASET_ID: Optional[str] = "nba_dataset"
    snowflake_account: Optional[str] = None
    snowflake_user: Optional[str] = None
    snowflake_password: Optional[str] = None
    snowflake_warehouse: Optional[str] = None
    snowflake_database: Optional[str] = None
    snowflake_schema: Optional[str] = None
    snowflake_rsa_private_key_path: Optional[str] = None
    DB_USER: str = "admin"
    DB_PASSWORD: str = "admin"
    DB_NAME: str = "backend_db"
    DB_HOST: str = "postgres-host-1"

settings = Settings()
