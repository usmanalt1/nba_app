from services.db.async_db import db_thread
from datetime import date, datetime
from typing import Dict, List, Optional

from ninja import Router, Schema

from app.models import MlModels
from config.logger import get_logger
from services.ml_model.models.model_trainer import ModelTraner, MODE_BACKTEST
from services.ml_model.prediction_history import read_graded
from services.redis.redis_client import RedisClient
from services.redis.redis_key_constants import (
    model_run_cache_key, user_run_cache_key, user_last_run_key, LAST_RUN,
)
from ninja_jwt.authentication import AsyncJWTAuth

logger = get_logger(__name__)

router = Router(auth=AsyncJWTAuth(), tags=["ml"])

# Nothing durable backs a Wormhole run, so this cache is its whole lifetime.
MODEL_CACHE_TTL_SECONDS = 24 * 60 * 60


class ModelOutput(Schema):
    game_id: str
    actual_home_win: Optional[bool] = None
    home_win_probability: float
    predicted_home_win: bool
    matchup: str
    home_team_name: str
    game_date: datetime
    season: str
    season_type: str

class ModelSeasonOutput(Schema):
    team: str  
    wins: int
    loss: int  
    season: str
    season_type: str


class ModelRunResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    season_records: Optional[List[ModelSeasonOutput]] = None
    predictions: Optional[List[ModelOutput]] = None
    warnings: Optional[List[str]] = None

class ModelLastRunResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    strategy: Optional[str] = None
    season: Optional[str] = None
    season_type: Optional[str] = None
    mode: Optional[str] = None



@router.get("/train/{strategy}/{season}/{season_type}", response=ModelRunResponseSchema)
async def train_model(request, strategy: str, season: str, season_type: str, mode: str = MODE_BACKTEST):
    try:
        redis_client = RedisClient()
        user_id = request.user.id
        def sync_train():
            trainer = ModelTraner(strategy=strategy, season=season, season_type=season_type, mode=mode)
            result = trainer.train()
            redis_client.set(
                user_run_cache_key(user_id, strategy, season, season_type, mode),
                result, ex=MODEL_CACHE_TTL_SECONDS,
            )
            redis_client.set(
                user_last_run_key(user_id),
                {"strategy": strategy, "season": season, "season_type": season_type, "mode": mode},
            )
            return result

        result = await db_thread(sync_train)
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return ModelRunResponseSchema(success=False, error=str(e))

    return ModelRunResponseSchema(
        success=True,
        metrics=result.metrics,
        season_records=result.season_record.to_dict(orient="records"),
        predictions=result.predictions.to_dict(orient="records"),
        warnings=result.warnings,
    )

@router.get("/get_ml_trained_models/{strategy}/{season}/{season_type}", response=ModelRunResponseSchema)
def get_latest_trained_models(request, strategy: str, season: str, season_type: str):
    try:
        result = RedisClient().get(model_run_cache_key(strategy, season, season_type))
    except Exception as e:
        logger.error(f"Error fetching latest trained models: {e}")
        return ModelRunResponseSchema(success=False, error=str(e))

    if not result:
        return ModelRunResponseSchema(success=False)

    return ModelRunResponseSchema(
        success=True,
        metrics=result.metrics,
        season_records=result.season_record.to_dict(orient="records"),
        predictions=result.predictions.to_dict(orient="records"),
        # older cached runs were pickled before `warnings` existed on TrainResult
        warnings=getattr(result, "warnings", None),
    )

@router.get("/get_last_run", response=ModelLastRunResponseSchema)
def get_last_run(request):
    try:
        last_run = RedisClient().get(LAST_RUN)
    except Exception as e:
        logger.error(f"Error fetching last run: {e}")
        return ModelLastRunResponseSchema(success=False, error=str(e))

    if not last_run:
        return ModelLastRunResponseSchema(success=False)

    return ModelLastRunResponseSchema(
        success=True,
        strategy=last_run.get("strategy"),
        season=last_run.get("season"),
        season_type=last_run.get("season_type"),
        mode=last_run.get("mode"),
    )

@router.get("/get_user_run/{strategy}/{season}/{season_type}", response=ModelRunResponseSchema)
def get_user_run(request, strategy: str, season: str, season_type: str, mode: str = MODE_BACKTEST):
    """The caller's own last run of these exact settings, if it has not expired."""
    try:
        result = RedisClient().get(
            user_run_cache_key(request.user.id, strategy, season, season_type, mode)
        )
    except Exception as e:
        logger.error(f"Error fetching user run: {e}")
        return ModelRunResponseSchema(success=False, error=str(e))

    if not result:
        return ModelRunResponseSchema(success=False)

    return ModelRunResponseSchema(
        success=True,
        metrics=result.metrics,
        season_records=result.season_record.to_dict(orient="records"),
        predictions=result.predictions.to_dict(orient="records"),
        warnings=result.warnings,
    )

@router.get("/get_user_last_run", response=ModelLastRunResponseSchema)
def get_user_last_run(request):
    """The settings the caller last ran, to reopen Wormhole where they left it."""
    try:
        last_run = RedisClient().get(user_last_run_key(request.user.id))
    except Exception as e:
        logger.error(f"Error fetching user last run: {e}")
        return ModelLastRunResponseSchema(success=False, error=str(e))

    if not last_run:
        return ModelLastRunResponseSchema(success=False)

    return ModelLastRunResponseSchema(
        success=True,
        strategy=last_run.get("strategy"),
        season=last_run.get("season"),
        season_type=last_run.get("season_type"),
        mode=last_run.get("mode"),
    )

class PredictionHistoryOutput(Schema):
    game_id: str
    game_date: Optional[date] = None
    season: str
    season_type: str
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    matchup: str
    home_win_probability: float
    predicted_home_win: bool
    # null until played
    actual_home_win: Optional[bool] = None


class PredictionHistoryResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    predictions: Optional[List[PredictionHistoryOutput]] = None


@router.get("/prediction_history/{strategy}/{season}/{season_type}", response=PredictionHistoryResponseSchema)
async def prediction_history(request, strategy: str, season: str, season_type: str, graded_only: bool = False):
    """Stored predictions with results joined on; unplayed games have actual_home_win null."""
    try:
        def sync_get():
            return read_graded(
                strategy=strategy, season=season, season_type=season_type,
                graded_only=graded_only,
            )

        records = await db_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}")
        return PredictionHistoryResponseSchema(success=False, error=str(e))

    return PredictionHistoryResponseSchema(success=True, predictions=records)


class MlModelOutput(Schema):
    model_name: str


class MlModelsResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    models: Optional[List[MlModelOutput]] = None


@router.get("/get_ml_models", response=MlModelsResponseSchema)
async def get_ml_models(request):
    try:
        def sync_get_models():
            return list(MlModels.objects.values("model_name"))

        models = await db_thread(sync_get_models)
    except Exception as e:
        logger.error(f"Error fetching ml models: {e}")
        return MlModelsResponseSchema(success=False, error=str(e))

    return MlModelsResponseSchema(success=True, models=models)


class ModelRunSummary(Schema):
    strategy: str
    season: str
    season_type: str
    metrics: Dict[str, float]


class ModelRunsResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    runs: Optional[List[ModelRunSummary]] = None


@router.get("/get_all_runs", response=ModelRunsResponseSchema)
async def get_all_runs(request):
    try:
        redis_client = RedisClient()

        def sync_get():
            runs = []
            for key in redis_client.keys("model:*"):
                parts = key.split(":")
                if len(parts) != 4:
                    continue
                _, strategy, season, season_type = parts
                result = redis_client.get(key)
                # live runs predict unplayed games only, so they are never scored
                if result is None or result.metrics is None:
                    continue
                runs.append(ModelRunSummary(strategy=strategy, season=season, season_type=season_type, metrics=result.metrics))

            runs.sort(key=lambda r: (r.season, r.strategy), reverse=True)
            return runs

        runs = await db_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching all runs: {e}")
        return ModelRunsResponseSchema(success=False, error=str(e))

    return ModelRunsResponseSchema(success=True, runs=runs)