import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from ninja import Router, Schema

from app.models import MlModels
from config.logger import get_logger
from services.ml_model.models.model_trainer import ModelTraner, MODE_BACKTEST
from services.redis.redis_client import RedisClient
from services.redis.redis_key_constants import model_run_cache_key, LAST_RUN
from ninja_jwt.authentication import AsyncJWTAuth

logger = get_logger(__name__)

router = Router(auth=AsyncJWTAuth(), tags=["ml"])

# cached TrainResults never expired before this - a fix to the model/feature pipeline, or
# the underlying data simply changing (dim_games gaining/losing rows on a later
# ingestion run), left stale results sitting under the same strategy+season key
# indefinitely, with nothing forcing a refresh until someone happened to re-run that
# exact strategy+season. 6h keeps results fresh across a game day without refitting on
# every request.
MODEL_CACHE_TTL_SECONDS = 6 * 60 * 60


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
        def sync_train():
            trainer = ModelTraner(strategy=strategy, season=season, season_type=season_type, mode=mode)
            result = trainer.train()
            redis_client.set(model_run_cache_key(strategy, season), result, ex=MODEL_CACHE_TTL_SECONDS)
            redis_client.set(LAST_RUN, {"strategy": strategy, "season": season, "season_type": season_type, "mode": mode})
            return result

        result = await asyncio.to_thread(sync_train)
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

@router.get("/get_ml_trained_models/{strategy}/{season}", response=ModelRunResponseSchema)
def get_latest_trained_models(request, strategy: str, season: str):
    try:
        result = RedisClient().get(model_run_cache_key(strategy, season))
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

        models = await asyncio.to_thread(sync_get_models)
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
            # cache keys are "{strategy}_{season}_model" (see model_run_cache_key) - season
            # strings like "2025-26" never contain an underscore, so splitting on the last
            # underscore reliably separates it from a strategy name that might (e.g.
            # "logistic_regression")
            for key in redis_client.keys("*_model"):
                strategy, _, season = key.removesuffix("_model").rpartition("_")
                if not strategy:
                    continue
                result = redis_client.get(key)
                if result is None or result.metrics is None:
                    continue
                runs.append(ModelRunSummary(strategy=strategy, season=season, season_type=result.season_type, metrics=result.metrics))

            runs.sort(key=lambda r: (r.season, r.strategy), reverse=True)
            return runs

        runs = await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching all runs: {e}")
        return ModelRunsResponseSchema(success=False, error=str(e))

    return ModelRunsResponseSchema(success=True, runs=runs)