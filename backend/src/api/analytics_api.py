from ninja import Router
from typing import Optional, List, Dict, Any
from ninja import Schema
import asyncio
import logging
import pandas as pd
logger = logging.getLogger(__name__)
from services.analytics.player_stats import PlayerStats
from services.analytics.team_stats import TeamStats
from services.analytics.most_improved import MostImprovedPlayers, MostImprovedTeams
from app.models import DimPlayers, FctPlayerStats, DimSeasons, DimTeams, DimGames, FctTeamStats
from ninja_jwt.authentication import AsyncJWTAuth

router = Router(auth=AsyncJWTAuth(), tags=["analytics"])

class NBADataResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None

@router.get("/average_stats", response=NBADataResponseSchema)
async def get_average_player_stats(request):

    try:
        def sync_get():
            logger.info("Fetching average player stats from the database...")

            # Fetch player stats, player info, and team info from the database to df
            player_stats_df = pd.DataFrame(list(
                FctPlayerStats.objects.values(
                    "season_id", "player_id", "pts", "reb", "plus_minus", "ast", "dreb", "oreb", "team_id", "season"
                )
            ))
            players_info_df = pd.DataFrame(list(
                DimPlayers.objects
                    .values("player_id", "season_id", "player_name")
            ))
            teams_info_df = pd.DataFrame(list(
                DimTeams.objects.values("team_id", "team_name")
            ))
            average_player_stats_df = PlayerStats(player_stats_df, players_info_df, teams_info_df).transform()
            average_player_stats_df = average_player_stats_df.where(pd.notnull(average_player_stats_df), None)
            average_players_stats_dict = average_player_stats_df.to_dict(orient="records")
            return NBADataResponseSchema(success=True, records=average_players_stats_dict)

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching average player stats: {e}")
        return NBADataResponseSchema(success=False, error=str(e))


@router.get("/average_team_stats", response=NBADataResponseSchema)
async def get_average_team_stats(request):

    try:
        def sync_get():
            logger.info("Fetching average team stats from the database...")

            team_stats_df = pd.DataFrame(list(
                FctTeamStats.objects.values(
                    "season_id", "team_id", "pts", "reb", "plus_minus", "ast", "season", "wl"
                )
            ))
            teams_info_df = pd.DataFrame(list(
                DimTeams.objects.values("team_id", "team_name")
            ))
            average_team_stats_df = TeamStats(team_stats_df, teams_info_df).transform()
            average_team_stats_df = average_team_stats_df.where(pd.notnull(average_team_stats_df), None)
            average_team_stats_dict = average_team_stats_df.to_dict(orient="records")
            return NBADataResponseSchema(success=True, records=average_team_stats_dict)

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching average team stats: {e}")
        return NBADataResponseSchema(success=False, error=str(e))


@router.get("/most_improved_players", response=NBADataResponseSchema)
async def get_most_improved_players(request):

    try:
        def sync_get():
            logger.info("Fetching most improved players from the database...")

            player_stats_df = pd.DataFrame(list(
                FctPlayerStats.objects.values("season_id", "player_id", "team_id", "pts", "season")
            ))
            players_info_df = pd.DataFrame(list(
                DimPlayers.objects.values("player_id", "season_id", "player_name")
            ))
            teams_info_df = pd.DataFrame(list(
                DimTeams.objects.values("team_id", "team_name")
            ))
            most_improved_df = MostImprovedPlayers(player_stats_df, players_info_df, teams_info_df).transform()
            most_improved_df = most_improved_df.where(pd.notnull(most_improved_df), None)
            return NBADataResponseSchema(success=True, records=most_improved_df.to_dict(orient="records"))

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching most improved players: {e}")
        return NBADataResponseSchema(success=False, error=str(e))


@router.get("/most_improved_teams", response=NBADataResponseSchema)
async def get_most_improved_teams(request):

    try:
        def sync_get():
            logger.info("Fetching most improved teams from the database...")

            team_stats_df = pd.DataFrame(list(
                FctTeamStats.objects.values("season_id", "team_id", "season", "wl")
            ))
            teams_info_df = pd.DataFrame(list(
                DimTeams.objects.values("team_id", "team_name")
            ))
            most_improved_df = MostImprovedTeams(team_stats_df, teams_info_df).transform()
            most_improved_df = most_improved_df.where(pd.notnull(most_improved_df), None)
            return NBADataResponseSchema(success=True, records=most_improved_df.to_dict(orient="records"))

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching most improved teams: {e}")
        return NBADataResponseSchema(success=False, error=str(e))