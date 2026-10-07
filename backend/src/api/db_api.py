from ninja import Router
from typing import Optional, List, Dict, Any, Literal
from ninja import Schema
import logging
logger = logging.getLogger(__name__)
from services.db.service import Service
from app.models import (
    DimPlayers, FctPlayerStats, FctTeamStats, FctAdvancedPlayerSeasonStats,
    FctAdvancedTeamSeasonStats, DimSeasons, DimTeams, DimGames,
)
import asyncio
from datetime import datetime
from ninja_jwt.authentication import AsyncJWTAuth

router = Router(auth=AsyncJWTAuth(), tags=["nba"])

class PlayerOption(Schema):
    player_id: int
    player_name: str

class SeasonOption(Schema):
    season_id: str
    season_name: str

class TeamOption(Schema):
    team_id: int
    team_name: str

class BoxScoreAverages(Schema):
    """Per-game averages shared by the player and team stat responses."""
    games_played: int
    average_minutes: Optional[float] = None
    average_points: Optional[float] = None
    average_field_goals_made: Optional[float] = None
    average_field_goals_attempted: Optional[float] = None
    field_goal_pct: Optional[float] = None
    average_three_pointers_made: Optional[float] = None
    average_three_pointers_attempted: Optional[float] = None
    three_point_pct: Optional[float] = None
    average_free_throws_made: Optional[float] = None
    average_free_throws_attempted: Optional[float] = None
    free_throw_pct: Optional[float] = None
    average_offensive_rebounds: Optional[float] = None
    average_defensive_rebounds: Optional[float] = None
    average_rebounds: Optional[float] = None
    average_assists: Optional[float] = None
    average_steals: Optional[float] = None
    average_blocks: Optional[float] = None
    average_turnovers: Optional[float] = None
    average_fouls: Optional[float] = None
    average_plus_minus: Optional[float] = None


class SeasonPlayerStats(BoxScoreAverages):
    player_id: int
    player_name: str
    season: str
    position: Optional[str] = None

class SeasonTeamStats(BoxScoreAverages):
    team_id: int
    team_name: str
    season: str
    wins: int
    losses: int

class AdvancedAverages(Schema):
    """Season-level advanced metrics. Shares are 0-100, matching the basic stats;
    ratings, pace and the assist/turnover ratios are raw per-game values."""
    games_played: Optional[int] = None
    wins: Optional[int] = None
    losses: Optional[int] = None
    average_minutes: Optional[float] = None
    offensive_rating: Optional[float] = None
    defensive_rating: Optional[float] = None
    net_rating: Optional[float] = None
    true_shooting_percentage: Optional[float] = None
    effective_field_goal_percentage: Optional[float] = None
    usage_percentage: Optional[float] = None
    assist_percentage: Optional[float] = None
    assist_to_turnover: Optional[float] = None
    assist_ratio: Optional[float] = None
    turnover_percentage: Optional[float] = None
    offensive_rebound_percentage: Optional[float] = None
    defensive_rebound_percentage: Optional[float] = None
    rebound_percentage: Optional[float] = None
    pace: Optional[float] = None
    possessions: Optional[float] = None
    pie: Optional[float] = None

class SeasonAdvancedPlayerStats(AdvancedAverages):
    player_id: int
    player_name: Optional[str] = None
    season: str
    position: Optional[str] = None
    team_abbreviation: Optional[str] = None
    age: Optional[float] = None

class SeasonAdvancedTeamStats(AdvancedAverages):
    team_id: int
    team_name: Optional[str] = None
    season: str

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
    home_pts: int
    away_pts: int


class NBADataResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None

@router.get("/list_players", response=List[PlayerOption])
async def list_players_filtered(request, season_name: Optional[str] = None, team_id: Optional[int] = None):
    """Players for a season and/or team; both omitted returns every player."""
    def sync_get():
        return Service(DimPlayers).get_all_players(season_name=season_name, team_id=team_id)
    return await asyncio.to_thread(sync_get)

@router.get("/season_player_stats", response=List[SeasonPlayerStats])
async def season_player_stats(
    request,
    season_name: str,
    team_id: Optional[int] = None,
    position: Optional[str] = None,
    season_type: Literal["regular", "playoffs", "preseason"] = "regular",
):
    """Regular season or playoff averages for every player in a season.

    Optionally narrowed by team or position. The two season types are separate
    sets of games, never combined.
    """
    def sync_get():
        return Service(FctPlayerStats).get_season_player_stats(
            season_name=season_name,
            team_id=team_id,
            position=position,
            season_type=season_type,
        )
    return await asyncio.to_thread(sync_get)

@router.get("/season_team_stats", response=List[SeasonTeamStats])
async def season_team_stats(
    request,
    season_name: str,
    team_id: Optional[int] = None,
    season_type: Literal["regular", "playoffs", "preseason"] = "regular",
):
    """Regular season or playoff averages and record for each team in a season."""
    def sync_get():
        return Service(FctTeamStats).get_season_team_stats(
            season_name=season_name, team_id=team_id, season_type=season_type,
        )
    return await asyncio.to_thread(sync_get)

@router.get("/season_advanced_player_stats", response=List[SeasonAdvancedPlayerStats])
async def season_advanced_player_stats(
    request,
    season_name: str,
    team_id: Optional[int] = None,
    position: Optional[str] = None,
    season_type: Literal["regular", "playoffs", "preseason"] = "regular",
):
    """Advanced season stats for every player in a season."""
    def sync_get():
        return Service(FctAdvancedPlayerSeasonStats).get_season_advanced_player_stats(
            season_name=season_name, team_id=team_id, position=position, season_type=season_type,
        )
    return await asyncio.to_thread(sync_get)

@router.get("/season_advanced_team_stats", response=List[SeasonAdvancedTeamStats])
async def season_advanced_team_stats(
    request,
    season_name: str,
    team_id: Optional[int] = None,
    season_type: Literal["regular", "playoffs", "preseason"] = "regular",
):
    """Advanced season stats for every team in a season."""
    def sync_get():
        return Service(FctAdvancedTeamSeasonStats).get_season_advanced_team_stats(
            season_name=season_name, team_id=team_id, season_type=season_type,
        )
    return await asyncio.to_thread(sync_get)

@router.get("/list_all_seasons", response=List[SeasonOption])
async def list_seasons(
    request,
    has_stats: bool = False,
    season_type: Literal["regular", "playoffs", "preseason"] = "regular",
):
    """Every season, or with has_stats=true only those with games of `season_type`."""
    def sync_get():
        service = Service(DimSeasons)
        return service.get_seasons_with_stats(season_type=season_type) if has_stats else service.get_all_seasons()
    return await asyncio.to_thread(sync_get)

@router.get("/list_all_teams", response=List[TeamOption])
async def list_teams(request):
    def sync_get():
        return Service(DimTeams).get_all_teams()
    return await asyncio.to_thread(sync_get)


@router.get("/get_player/{player_id}", response= List[PlayerAggStats])
async def get_player(request, player_id: int, season_type: Literal["regular", "playoffs", "preseason"] = "regular"):
    """One player's averages per season, for the given season type."""
    def sync_get_player(player_id: int):
        return Service(FctPlayerStats).get_player_stats(
            player_id=player_id, season_type=season_type,
        )

    return await asyncio.to_thread(sync_get_player, player_id)

@router.get("/get_top_3_best_players_latest_season/{stat_type}", response=List[PlayerAggStats])
async def get_top_3_best_players_latest_season(request, stat_type: str):
    def sync_get_top_3_best_players_latest_season():
        # Seasons with recorded games only: dim_seasons also carries the upcoming
        # season, which has no stats and would make this return nothing.
        latest_season: DimSeasons = Service(DimSeasons).get_seasons_with_stats()[-1]
        season_name = latest_season.season_name
        players_stats = Service(FctPlayerStats).get_player_stats(season_id=season_name)
        filtered_stats = [stat for stat in players_stats if stat['season'] == season_name]
        sorted_stats = sorted(filtered_stats, key=lambda x: x[f'average_{stat_type}'], reverse=True)
        return sorted_stats[:3]

    return await asyncio.to_thread(sync_get_top_3_best_players_latest_season)

@router.get("/get_latest_games/season={season_name}/season_type={season_type}", response=List[LatestGames])
async def latest_games(request, season_name: str, season_type: str):
    def sync_latest_games():
        return Service(DimGames).get_latest_games(season=season_name, season_type=season_type)

    return await asyncio.to_thread(sync_latest_games)





