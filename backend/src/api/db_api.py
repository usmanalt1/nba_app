from ninja import Router
from typing import Optional, List, Dict, Any
from ninja import Schema
import logging
logger = logging.getLogger(__name__)
from services.db.service import Service
from app.models import DimPlayers, FctPlayerStats, DimSeasons, DimTeams
import asyncio
from api import schemas

router = Router()

class PlayerOption(Schema):
    player_id: int
    player_name: str

class SeasonOption(Schema):
    season_id: str
    season_name: str

class TeamOption(Schema):
    team_id: int
    team_name: str

class PlayerAggStats(Schema):
    player_id: int
    season_id: int
    average_points: float
    average_rebounds: float
    average_plus_minus: float
    average_assists: float

class NBADataResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None

@router.get("/list_all_players/{season_name}/{team_id}", response=List[PlayerOption])
async def list_players(request, season_name: str, team_id: int):
    def sync_get():
        return Service(DimPlayers).get_all_players(season_name=season_name, team_id=team_id)
    return await asyncio.to_thread(sync_get)

@router.get("/list_all_seasons", response=List[SeasonOption])
async def list_seasons(request):
    def sync_get():
        return Service(DimSeasons).get_all_seasons()
    return await asyncio.to_thread(sync_get)

@router.get("/list_all_teams", response=List[TeamOption])
async def list_teams(request):
    def sync_get():
        return Service(DimTeams).get_all_teams()
    return await asyncio.to_thread(sync_get)


@router.get("/get_player/{player_id}", response= List[PlayerAggStats])
async def get_player(request, player_id: int):
    def sync_get_player(player_id: int):
        return Service(FctPlayerStats).get_player_stats(player_id=player_id)

    return await asyncio.to_thread(sync_get_player, player_id)





