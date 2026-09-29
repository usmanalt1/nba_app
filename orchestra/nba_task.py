"""Standalone entry points for the NBA pipeline's non-dbt steps.

These are the same steps the Django API exposes, minus the API: no web server, no
JWT, no tunnel. Orchestra runs this file directly from git with a PYTHON /
PYTHON_EXECUTE_SCRIPT task, and it works identically from a shell or a Cloud Run
job, which makes it testable locally without any deployment.

    python orchestra/nba_task.py collect --season-year 2024-25
    python orchestra/nba_task.py collect --season-year 2024-25 --seasons 3
    python orchestra/nba_task.py load-bigquery --seasons 2024-25

Why this exists rather than an HTTP task: the API's handlers catch exceptions and
return HTTP 200 with {"success": false}, and Orchestra fails a task only on a
non-2xx status - so a failed collect reports SUCCEEDED and dbt then transforms
stale data. This script has no such layer. It raises, exits non-zero, and the task
goes red, which is the behaviour an orchestrator needs.

Only `build_nba_data` is used here, which is deliberately Django-free - the ORM
imports live inside `build_player_awards`. So this needs no django.setup() and no
database connection, just the settings that ObjectStorageService reads.

Configuration, and why it matters on a cloud runner: `.env` and the service-account
JSON are both gitignored, so neither exists in the repo Orchestra clones. Without
help, pydantic-settings falls back to its defaults - including STORAGE="local" -
and collect would write parquet to an ephemeral disk and report success. So:

  * pass STORAGE, PARENT_BUCKET, GCS_PROJECT_NAME, FILE_FORMAT and
    BIGQUERY_DATASET_ID as environment variables (Orchestra: environment_variables)
  * pass the key as GCS_SERVICE_ACCOUNT_JSON_CONTENT, the JSON itself rather than a
    path - the code wants a file, so this script writes it to a temp file and
    repoints GCS_SERVICE_ACCOUNT_JSON at it
  * pass --expect-storage gcs, which fails the task if the resolved backend is not
    the one you meant, instead of quietly writing somewhere useless
"""

import argparse
import json
import logging
import os
import sys
import tempfile
from pathlib import Path

# The services package is not installed, it is imported from the repo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend" / "src"))

logger = logging.getLogger("nba_task")


def materialise_credentials():
    """Write GCS_SERVICE_ACCOUNT_JSON_CONTENT to a file, if it is set.

    ObjectStorageService and BigQueryService both want a path on disk
    (`from_service_account_json`, `gcsfs(token=...)`), but a cloud runner can only
    be handed a secret as a string. Bridge the two here rather than changing the
    services, so nothing about the local path changes.
    """
    content = os.environ.get("GCS_SERVICE_ACCOUNT_JSON_CONTENT")
    if not content:
        return
    try:
        json.loads(content)
    except ValueError as exc:
        raise ValueError(f"GCS_SERVICE_ACCOUNT_JSON_CONTENT is not valid JSON: {exc}")

    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", prefix="gcs-key-", delete=False
    )
    with handle as f:
        f.write(content)
    os.environ["GCS_SERVICE_ACCOUNT_JSON"] = handle.name
    logger.info("wrote service-account key from env to %s", handle.name)


def resolve_storage(expect=None):
    """Build the storage backend, optionally asserting which one it is.

    The guard exists because ObjectStorageService silently falls back to
    LocalStorage for any unrecognised STORAGE value - on an ephemeral runner that
    means the data is written and then thrown away, with a green task.
    """
    from services.object_storage.service import ObjectStorageService

    storage = ObjectStorageService().get_storage()
    name = type(storage).__name__
    logger.info("object storage backend: %s (STORAGE=%s)",
                name, os.environ.get("STORAGE", "<unset, default 'local'>"))
    if expect:
        wanted = {"gcs": "GCSStorage", "az": "AzureBlobStorage", "local": "LocalStorage"}[expect]
        if name != wanted:
            raise RuntimeError(
                f"--expect-storage {expect} requires {wanted}, but resolved {name}. "
                f"STORAGE={os.environ.get('STORAGE', '<unset>')!r} - on a cloud runner "
                f".env is not in the repo, so STORAGE must be passed as an environment "
                f"variable."
            )
    return storage


def split_season(season_year):
    """Validate and split "2024-25" into ("2024", "25")."""
    parts = str(season_year).split("-")
    if (len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 2
            or not all(p.isdigit() for p in parts)):
        raise ValueError(f"season_year must look like '2024-25', got {season_year!r}")
    return parts[0], parts[1]


def season_id_for(season_year):
    """"2024-25" -> "24025".

    Odd-looking, but it reproduces exactly what the API handlers compute, so the
    two paths collect the same thing. Do not "fix" it here alone.
    """
    start, end = split_season(season_year)
    return f"{start[-2:]}0{end[-2:]}"


def previous_season_year(season_year):
    """"2024-25" -> "2023-24"."""
    start, end = split_season(season_year)
    return f"{int(start) - 1}-{str(int(end) - 1).zfill(2)[-2:]}"


def collect(season_year, seasons, team_roster, expect_storage=None):
    """Collect one or more seasons into object storage.

    Mirrors the /collect/season/... endpoints, but synchronously: the API's
    multi-season handler detaches the work with asyncio.create_task and responds
    before it finishes, which no orchestrator can wait on correctly.
    """
    import pandas as pd
    from services.data_collection.build_data_service import BuildDataService

    storage = resolve_storage(expect_storage)

    # One timestamp for the whole invocation, so the staging models'
    # get_latest_by_run_timestamp macro treats these seasons as a single run.
    run_timestamp = pd.Timestamp.now()
    collected = {}

    for _ in range(seasons):
        season_id = season_id_for(season_year)
        logger.info("collecting season %s (id %s)", season_year, season_id)
        tables = BuildDataService().build_nba_data(
            season_id=season_id,
            season_year=season_year,
            team_roster=team_roster,
        )
        if not tables:
            raise RuntimeError(f"no tables returned for season {season_year}")

        for table_name, df in tables.items():
            df["run_timestamp"] = run_timestamp
            storage.save(df=df, file_name=table_name, season=season_year)
            logger.info("saved %s (%d rows) for %s", table_name, len(df), season_year)

        collected[season_year] = sorted(tables)
        season_year = previous_season_year(season_year)

    total = sum(len(v) for v in collected.values())
    logger.info("collected %d table(s) across %d season(s)", total, len(collected))
    return collected


def load_bigquery(seasons, expect_storage=None):
    """Load the latest object-storage run into BigQuery.

    Appends, which is intentional: every staging model dedupes on run_timestamp via
    the get_latest_by_run_timestamp macro, so re-running a season supersedes it.
    """
    # BigQueryService reads .storage_client off the storage backend, which only
    # GCSStorage has - so this step cannot work on any other backend. Assert it up
    # front rather than failing later with an opaque AttributeError.
    resolve_storage(expect_storage or "gcs")
    from services.warehouse_storage.bigquery.service import BigQueryService

    logger.info("loading seasons %s from GCS into BigQuery", seasons)
    BigQueryService().load_latest_data_from_gcs_to_bigquery(seasons=seasons)
    logger.info("load complete")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="step", required=True)

    p_collect = sub.add_parser("collect", help="collect season(s) into object storage")
    p_collect.add_argument("--season-year", required=True, help='e.g. "2024-25"')
    p_collect.add_argument("--seasons", type=int, default=1,
                           help="how many seasons to walk back (default 1)")
    p_collect.add_argument("--team-roster", action="store_true",
                           help="also collect team rosters")

    p_load = sub.add_parser("load-bigquery", help="load object storage into BigQuery")
    p_load.add_argument("--seasons", required=True,
                        help='comma-separated, e.g. "2024-25,2023-24"')

    for sp in (p_collect, p_load):
        sp.add_argument("--expect-storage", choices=["gcs", "az", "local"],
                        help="fail unless the resolved storage backend is this one")

    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s %(message)s",
    )

    # No try/except: a traceback and a non-zero exit are exactly what the
    # orchestrator should see. Wrapping this is what makes the API unorchestratable.
    materialise_credentials()

    if args.step == "collect":
        if args.seasons < 1:
            parser.error("--seasons must be at least 1")
        collect(args.season_year, args.seasons, args.team_roster, args.expect_storage)
    else:
        seasons = [s.strip() for s in args.seasons.split(",") if s.strip()]
        if not seasons:
            parser.error("--seasons must list at least one season")
        load_bigquery(seasons, args.expect_storage)

    return 0


if __name__ == "__main__":
    sys.exit(main())
