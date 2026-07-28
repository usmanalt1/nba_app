import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from ninja import Router, Schema

from config.logger import get_logger
from services.ml_model.models.model_trainer import ModelTraner

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



@router.get("/train/{strategy}/{season}", response=ModelRunResponseSchema)
async def train_model(request, strategy: str, season: str):
    try:
        def sync_train():
            trainer = ModelTraner(strategy=strategy, season=season)
            return trainer.train()

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
