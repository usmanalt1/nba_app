import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from ninja import Router, Schema

from app.models import MlModels
from config.logger import get_logger
from services.ml_model.models.model_trainer import ModelTraner
from services.redis.redis_client import RedisClient
from services.redis.redis_key_constants import model_run_cache_key, LAST_RUN

logger = get_logger(__name__)

router = Router()


class ModelOutput(Schema):
    game_id: str
    season_id: int
    actual_home_win: bool
    home_win_probability: float
    predicted_home_win: bool
    matchup: str
    home_team_name: str
    game_date: datetime
    season: str

class ModelSeasonOutput(Schema):
    team: str  
    wins: int
    loss: int  
    season: str


class ModelRunResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    metrics: Optional[Dict[str, float]] = None
    season_records: Optional[List[ModelSeasonOutput]] = None
    predictions: Optional[List[ModelOutput]] = None

class ModelLastRunResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    strategy: Optional[str] = None
    season: Optional[str] = None



@router.get("/train/{strategy}/{season}", response=ModelRunResponseSchema)
async def train_model(request, strategy: str, season: str):
    try:
        redis_client = RedisClient()
        def sync_train():
            trainer = ModelTraner(strategy=strategy, season=season)
            result = trainer.train()
            redis_client.set(model_run_cache_key(strategy, season), result)
            redis_client.set(LAST_RUN, {"strategy": strategy, "season": season})
            return result

        result = await asyncio.to_thread(sync_train)
    except Exception as e:
        logger.error(f"Error training model: {e}")
        return ModelRunResponseSchema(success=False, error=str(e))

    return ModelRunResponseSchema(
        success=True,
        metrics=result.metrics,
        season_records=result.season_record.to_dict(orient="records"),
        predictions=result.predictions.to_dict(orient="records")
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

    return ModelLastRunResponseSchema(success=True, strategy=last_run.get("strategy"), season=last_run.get("season"))

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