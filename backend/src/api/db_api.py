from ninja import Router
from typing import Optional, List, Dict, Any
from ninja import Schema
import logging
logger = logging.getLogger(__name__)
from services.db.service import Service
from app.models import DimPlayers, FctPlayerStats, DimSeasons, DimTeams, DimGames
import asyncio
from datetime import datetime

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
    player_name: str
    season_id: int
    average_points: float
    average_rebounds: float
    average_plus_minus: float
    average_assists: float

class LatestGames(Schema):
    game_date: datetime
    season: str
    home_team_name: str
    away_team_name: str


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

@router.get("/get_top_3_best_players_latest_season/{stat_type}", response=List[PlayerAggStats])
async def get_top_3_best_players_latest_season(request, stat_type: str):
    def sync_get_top_3_best_players_latest_season():
        latest_season: DimSeasons = Service(DimSeasons).get_all_seasons()[-1]
        season_name = latest_season.season_name
        players_stats = Service(FctPlayerStats).get_player_stats(season_id=season_name)
        filtered_stats = [stat for stat in players_stats if stat['season'] == season_name]
        sorted_stats = sorted(filtered_stats, key=lambda x: x[f'average_{stat_type}'], reverse=True)
        return sorted_stats[:3]

    return await asyncio.to_thread(sync_get_top_3_best_players_latest_season)

@router.get("/get_latest_games", response=List[LatestGames])
async def latest_games(request):
    def sync_latest_games():
        latest_season: DimSeasons = Service(DimSeasons).get_all_seasons()[-1]
        return Service(DimGames).get_latest_games(season=latest_season.season_name)

    return await asyncio.to_thread(sync_latest_games)





