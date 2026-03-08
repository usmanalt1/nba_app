from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.cloud import storage
from config.settings import settings
from services.object_storage.service import ObjectStorageService
import pandas as pd
from typing import List, Tuple

from logging import getLogger
logger = getLogger(__name__)

class BigQueryService:
    def __init__(self, project: str = settings.GCS_PROJECT_NAME):
        self.client = bigquery.Client.from_service_account_json(
            settings.GCS_SERVICE_ACCOUNT_JSON, project=project
        )
        self.gcs_storage_client: storage.Client = ObjectStorageService().get_storage().storage_client
        self.settings = settings
    
    def load_latest_data_from_gcs_to_bigquery(self, seasons: list, dataset_id: str = settings.BIGQUERY_DATASET_ID) -> None:
        logger.info(f"Starting to load data from GCS to BigQuery for seasons: {seasons}")
        self._create_dataset(dataset_id=dataset_id)
        latest_file_names, latest_run_id = self._get_latest_gcs_files()
        for file_name in latest_file_names:
            df = ObjectStorageService().get_storage().read(latest_run_id=latest_run_id, seasons=seasons, table=file_name)
            table_id = file_name
            logger.info(f"Loading data for table {table_id} from GCS run_id {latest_run_id} to BigQuery dataset {dataset_id}.")
            self._load_dataframe_to_bigquery(
                df=df,
                dataset_id=dataset_id,
                table_id=table_id,
                project=self.settings.GCS_PROJECT_NAME,
                write_disposition="WRITE_TRUNCATE",
            )

    def _get_latest_gcs_files(self, bucket_name: str = settings.PARENT_BUCKET) -> Tuple[List[str], str]:
        # List all files in the bucket and find the latest run_id based on the folder structure
        # assume files are stored in the format: gs://bucket/run_id/season=season_id/file_name.parquet
        blobs = list(self.gcs_storage_client.list_blobs(bucket_name))
        latest_run_id = max([blob.name.split("/")[0] for blob in blobs])
        latest_files = [blob.name.split("/")[2].split('.')[0] for blob in blobs if blob.name.startswith(latest_run_id)]
        return list(set(latest_files)), latest_run_id
    

    def _create_dataset(self, dataset_id: str = settings.BIGQUERY_DATASET_ID) -> None:
        logger.info(f"Ensuring BigQuery dataset {dataset_id} exists.")
        dataset_ref = self.client.dataset(dataset_id)
        try:
            self.client.get_dataset(dataset_ref)
            logger.info(f"Dataset {dataset_id} already exists.")
        except NotFound:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            self.client.create_dataset(dataset)
            logger.info(f"Dataset {dataset_id} created.")

    def _load_dataframe_to_bigquery(
        self,
        df: pd.DataFrame,
        table_id: str,
        dataset_id: str = settings.BIGQUERY_DATASET_ID,
        project: str = settings.GCS_PROJECT_NAME,
        write_disposition: str = "WRITE_APPEND",
    ) -> None:
        client = bigquery.Client.from_service_account_json(self.settings.GCS_SERVICE_ACCOUNT_JSON, project=project)

        table_ref = f"{project}.{dataset_id}.{table_id}"

        job_config = bigquery.LoadJobConfig(
            write_disposition=write_disposition,
            autodetect=True,
        )

        load_job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        load_job.result()

        table = client.get_table(table_ref)

        logger.info(f"Loaded {table.num_rows} rows into {table_ref}.")