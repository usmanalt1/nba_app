"""Nightly pipeline: NBA API -> object storage -> Postgres -> dbt -> live predictions.

Postgres, not BigQuery: the Django models the API serves are managed=False views onto
nba_marts.*. bigquery_tables below is a separate analytics mirror.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

import django_setup  # noqa: F401  # must come before any backend import

from dagster import AssetExecutionContext, Config, MetadataValue, asset

from seasons import current_season, previous_season
from services.data_collection.build_data_service import BuildDataService
from services.db.db_service import DBService
from services.ml_model.models.model_trainer import ModelTraner, MODE_LIVE
from services.ml_model.prediction_history import persist_predictions
from services.redis.redis_client import RedisClient
from services.redis.redis_key_constants import model_run_cache_key, LAST_RUN
from services.warehouse_storage.bigquery.service import BigQueryService

REPO_ROOT = Path(__file__).resolve().parent.parent
DBT_PROJECT_DIR = REPO_ROOT / "pipeline_nba"

MODEL_CACHE_TTL_SECONDS = 6 * 60 * 60


class NightlyConfig(Config):
    # season_year None means derive from today - pinning it is how a pipeline ends up
    # stuck on last season.
    season_year: str = None
    strategies: list = ["logistic_regression", "random_forest"]
    season_types: list = ["preseason", "regular"]
    dbt_target: str = None


def _season(config) -> str:
    return config.season_year or current_season()


@asset(compute_kind="nba_api")
def latest_nba_data(context: AssetExecutionContext, config: NightlyConfig) -> dict:
    """Collect the in-progress season into object storage. Returns the run_id."""
    season_year = _season(config)
    context.log.info(f"Collecting latest data for {season_year}")

    result = BuildDataService().build_latest_data(season_year=season_year)

    context.add_output_metadata({
        "run_id": result["run_id"],
        "season": result["season_year"],
        "tables": MetadataValue.json(result["saved"]),
        "rows_collected": sum(result["saved"].values()),
    })
    return result


@asset(compute_kind="postgres")
def postgres_raw_tables(context: AssetExecutionContext, latest_nba_data: dict) -> dict:
    """Upsert this run's parquet files into the raw Postgres tables dbt reads from."""
    run_id = latest_nba_data["run_id"]
    context.log.info(f"Loading run {run_id} into Postgres")

    loaded = DBService().save(run_id=run_id)

    if not loaded:
        raise RuntimeError(
            f"Run {run_id} loaded no rows into Postgres. DBService reads parquet off the "
            "local filesystem only, so STORAGE must be 'local'."
        )

    context.add_output_metadata({
        "run_id": run_id,
        "tables": MetadataValue.json(loaded),
        "rows_loaded": sum(loaded.values()),
    })
    return loaded


@asset(compute_kind="dbt")
def dbt_marts(context: AssetExecutionContext, config: NightlyConfig, postgres_raw_tables: dict) -> dict:
    """Build the dbt project. `build` not `run`, so a failing test stops downstream models."""
    target = config.dbt_target or os.getenv("DBT_TARGET", "container_postgres")
    command = [
        "dbt", "build",
        "--project-dir", str(DBT_PROJECT_DIR),
        "--profiles-dir", str(DBT_PROJECT_DIR),
        "--target", target,
    ]
    context.log.info(f"Running: {' '.join(command)}")

    process = subprocess.run(command, cwd=str(DBT_PROJECT_DIR), capture_output=True, text=True)
    for line in process.stdout.splitlines():
        context.log.info(line)
    if process.stderr:
        context.log.warning(process.stderr)

    if process.returncode != 0:
        raise RuntimeError(f"dbt build failed against target '{target}' (exit {process.returncode})")

    context.add_output_metadata({
        "target": target,
        "summary": MetadataValue.md(f"```\n{process.stdout[-4000:]}\n```"),
    })
    return {"target": target, "returncode": process.returncode}


def _run_one(context: AssetExecutionContext, season: str, season_type: str, strategy: str) -> dict:
    """Train one strategy for one season type, cache it and store its predictions."""
    label = f"{strategy}/{season_type}"
    try:
        result = ModelTraner(
            strategy=strategy, season=season, season_type=season_type, mode=MODE_LIVE,
        ).train()
    except Exception as exc:
        # a season type with no games yet shouldn't fail the whole run
        context.log.warning(f"{label}: skipped - {exc}")
        return {"error": str(exc)}

    RedisClient().set(
        model_run_cache_key(strategy, season), result, ex=MODEL_CACHE_TTL_SECONDS,
    )
    stored = persist_predictions(
        strategy=strategy, season=season, season_type=season_type,
        predictions=result.predictions,
    )

    for warning in result.warnings or []:
        context.log.warning(f"{label}: {warning}")

    outcome = {"predicted": len(result.predictions), **stored}
    context.log.info(f"{label}: {outcome}")
    return outcome


def _pick_last_run(summary: dict, season: str) -> Optional[dict]:
    """The run the homepage opens on: the first that actually stored predictions.

    config.season_types is ordered preseason-first, so the homepage sits on the preseason
    while it has games left and moves to the regular season on its own once it doesn't.
    """
    for label, outcome in summary.items():
        if outcome.get("written"):
            strategy, season_type = label.split("/")
            return {
                "strategy": strategy, "season": season,
                "season_type": season_type, "mode": MODE_LIVE,
            }
    return None


@asset(compute_kind="python")
def live_predictions(context: AssetExecutionContext, config: NightlyConfig, dbt_marts: dict) -> dict:
    """Predict the upcoming slate for each strategy and season type.

    Predictions go to model_prediction_history as well as Redis: the cache is replaced
    tomorrow night, so without it there is nothing left to grade once games are played.
    """
    season = _season(config)
    summary = {}

    for season_type in config.season_types:
        for strategy in config.strategies:
            summary[f"{strategy}/{season_type}"] = _run_one(
                context, season=season, season_type=season_type, strategy=strategy,
            )

    last_run = _pick_last_run(summary, season)
    if last_run:
        RedisClient().set(LAST_RUN, last_run)
        context.log.info(f"LAST_RUN -> {last_run}")

    context.add_output_metadata({
        "season": season,
        "runs": MetadataValue.json(summary),
        "last_run": MetadataValue.json(last_run or {}),
    })
    return summary


@asset(compute_kind="bigquery")
def bigquery_tables(context: AssetExecutionContext, latest_nba_data: dict) -> dict:
    """Mirror the collected run into BigQuery. Analytics only; the API never reads it."""
    season = latest_nba_data["season_year"]
    context.log.info(f"Loading season {season} into BigQuery")

    BigQueryService().load_latest_data_from_gcs_to_bigquery(seasons=[season])

    context.log.info("Successfully loaded tables into BigQuery")
    return {"seasons": [season]}


class BacktestConfig(Config):
    # defaults to the last completed season
    season_year: str = None
    season_type: str = "regular"
    strategies: list = ["logistic_regression", "random_forest"]


@asset(compute_kind="python")
def backtest_scorecard(context: AssetExecutionContext, config: BacktestConfig, dbt_marts: dict) -> dict:
    """Score each strategy against a finished season. Live mode cannot do this - its
    predictions have no outcomes yet."""
    season = config.season_year or previous_season(current_season())
    redis_client = RedisClient()
    metrics = {}

    for strategy in config.strategies:
        context.log.info(f"Backtesting {strategy} on {season} ({config.season_type})")
        trainer = ModelTraner(strategy=strategy, season=season, season_type=config.season_type)
        result = trainer.train()
        redis_client.set(
            model_run_cache_key(strategy, season), result, ex=MODEL_CACHE_TTL_SECONDS,
        )
        metrics[strategy] = result.metrics
        for warning in result.warnings or []:
            context.log.warning(f"{strategy}: {warning}")

    context.add_output_metadata({"season": season, "metrics": MetadataValue.json(metrics)})
    return metrics
