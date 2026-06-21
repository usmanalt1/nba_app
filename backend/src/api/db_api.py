from ninja import Router
from typing import Optional, List, Dict, Any
from ninja import Schema
import logging
logger = logging.getLogger(__name__)
from asgiref.sync import sync_to_async
from services.db.service import Service
from app.models import PlayerInfo
import asyncio

router = Router()

class PlayerOption(Schema):
    id: int
    full_name: str

class NBADataResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None

@router.get("/list_all_players", response=List[PlayerOption])
async def list_players(request):
    def sync_get():
        return Service(PlayerInfo).get_all("full_name")
    return await asyncio.to_thread(sync_get)
    




