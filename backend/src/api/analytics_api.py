from ninja import Router
from typing import Optional, List, Dict, Any
from ninja import Schema
import asyncio
import logging
import pandas as pd
logger = logging.getLogger(__name__)
from services.analytics.player_stats import PlayerStats
from app.models import DimPlayers, FctPlayerStats, DimSeasons, DimTeams, DimGames


router = Router()

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