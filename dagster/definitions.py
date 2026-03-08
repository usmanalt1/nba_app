from dagster import Definitions, ScheduleDefinition, define_asset_job
from assets import raw_nba_data, bigquery_tables

nba_pipeline = define_asset_job("nba_pipeline", selection="*")

# Runs daily at 6am UTC — adjust cron as needed
nightly_schedule = ScheduleDefinition(
    job=nba_pipeline,
    cron_schedule="0 6 * * *",
)

defs = Definitions(
    assets=[raw_nba_data, bigquery_tables],
    schedules=[nightly_schedule],
)
