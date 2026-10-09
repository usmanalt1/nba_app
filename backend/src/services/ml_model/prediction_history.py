"""Durable store for live predictions, graded against dim_games at read time.

The Redis cache holds one run, so without this nothing survives to grade.
"""

from logging import getLogger

import pandas as pd
from django.utils import timezone

from app.models import DimGames, ModelPredictionHistory

logger = getLogger(__name__)

UNIQUE_FIELDS = ["strategy", "season", "season_type", "game_id"]

# mirrors api.model_api.PredictionHistoryOutput
_READ_FIELDS = [
    "game_id", "game_date", "season", "season_type", "home_team_name",
    "away_team_name", "home_win_probability", "predicted_home_win",
]


def _played_game_ids(season: str, season_type: str) -> set:
    return set(
        DimGames.objects.filter(season=season, season_type=season_type)
        .exclude(home_wl__isnull=True)
        .values_list("game_id", flat=True)
    )


def persist_predictions(strategy: str, season: str, season_type: str, predictions: pd.DataFrame) -> dict:
    """Upsert one row per predicted game, skipping played ones: the stored row was
    written before tip-off and overwriting it would be hindsight."""
    if predictions is None or predictions.empty:
        logger.info(f"No predictions to persist for {strategy}/{season}/{season_type}")
        return {"received": 0, "written": 0, "skipped_played": 0}

    already_played = _played_game_ids(season=season, season_type=season_type)
    fresh = predictions[~predictions["game_id"].isin(already_played)]
    skipped = len(predictions) - len(fresh)
    if skipped:
        logger.warning(
            f"Skipped {skipped} prediction(s) for {season} games that already have a "
            f"result - dim_games may have been stale when this ran"
        )

    if fresh.empty:
        return {"received": len(predictions), "written": 0, "skipped_played": skipped}

    predicted_at = timezone.now()
    rows = [
        ModelPredictionHistory(
            strategy=strategy,
            season=season,
            season_type=season_type,
            game_id=record["game_id"],
            game_date=record.get("game_date"),
            home_team_id=record.get("home_team_id"),
            home_team_name=record.get("home_team_name"),
            away_team_name=record.get("away_team_name"),
            home_win_probability=float(record["home_win_probability"]),
            predicted_home_win=bool(record["predicted_home_win"]),
            predicted_at=predicted_at,
        )
        for record in fresh.to_dict(orient="records")
    ]

    ModelPredictionHistory.objects.bulk_create(
        rows,
        update_conflicts=True,
        unique_fields=UNIQUE_FIELDS,
        update_fields=[
            "game_date", "home_team_id", "home_team_name", "away_team_name",
            "home_win_probability", "predicted_home_win", "predicted_at",
        ],
        batch_size=1000,
    )

    logger.info(f"Persisted {len(rows)} prediction(s) for {strategy}/{season}/{season_type}")
    return {"received": len(predictions), "written": len(rows), "skipped_played": skipped}


def read_graded(strategy: str, season: str, season_type: str, graded_only: bool = False) -> list:
    """Stored predictions with `actual_home_win` joined from dim_games, null if unplayed."""
    stored = list(
        ModelPredictionHistory.objects
        .filter(strategy=strategy, season=season, season_type=season_type)
        .order_by("game_date")
        .values(*_READ_FIELDS)
    )
    if not stored:
        return []

    results = dict(
        DimGames.objects
        .filter(season=season, season_type=season_type)
        .values_list("game_id", "home_wl")
    )

    records = []
    for row in stored:
        wl = results.get(row["game_id"])
        actual = None if wl is None else wl == "W"
        if graded_only and actual is None:
            continue
        records.append({
            **row,
            "actual_home_win": actual,
            "matchup": f"{row['home_team_name']} vs {row['away_team_name']}",
        })

    return records
