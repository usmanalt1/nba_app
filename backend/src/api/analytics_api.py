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

def _player_name_lookup() -> pd.DataFrame:
    """One row per player. dim_players has a row per (player, season) but the callers
    merge on player_id alone, which fans out every stat row."""
    df = pd.DataFrame(list(
        DimPlayers.objects.values("player_id", "player_name", "season").order_by("season")
    ))
    if df.empty:
        return pd.DataFrame(columns=["player_id", "player_name"])
    return df.drop_duplicates(subset=["player_id"], keep="last")[["player_id", "player_name"]]


def _team_name_lookup() -> pd.DataFrame:
    """One row per team. dim_teams has a row per (team, season) but the callers merge on
    team_id alone, which fans out every stat row. Newest row wins, so renames show current."""
    df = pd.DataFrame(list(
        DimTeams.objects.values("team_id", "team_name", "season").order_by("season")
    ))
    if df.empty:
        return pd.DataFrame(columns=["team_id", "team_name"])
    return df.drop_duplicates(subset=["team_id"], keep="last")[["team_id", "team_name"]]


@router.get("/average_stats/season={season_name}/season_type={season_type}", response=NBADataResponseSchema)
async def get_average_player_stats(request, season_name: str, season_type: str):

    try:
        def sync_get():
            logger.info("Fetching average player stats from the database...")

            # Fetch player stats, player info, and team info from the database to df
            player_stats_df = pd.DataFrame(list(
                FctPlayerStats.objects.filter(season=season_name, season_type=season_type).values(
                    "season_id", "player_id", "pts", "reb", "plus_minus", "ast", "dreb", "oreb", "team_id", "season", "season_type",
                )
            ))
            players_info_df = _player_name_lookup()
            teams_info_df = _team_name_lookup()
            average_player_stats_df = PlayerStats(player_stats_df, players_info_df, teams_info_df).transform()
            average_player_stats_df = average_player_stats_df.where(pd.notnull(average_player_stats_df), None)
            average_players_stats_dict = average_player_stats_df.to_dict(orient="records")
            return NBADataResponseSchema(success=True, records=average_players_stats_dict)

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching average player stats: {e}")
        return NBADataResponseSchema(success=False, error=str(e))


@router.get("/average_team_stats/season={season_name}/season_type={season_type}", response=NBADataResponseSchema)
async def get_average_team_stats(request, season_name: str, season_type: str):

    try:
        def sync_get():
            logger.info("Fetching average team stats from the database...")

            team_stats_df = pd.DataFrame(list(
                FctTeamStats.objects.filter(season=season_name, season_type=season_type).values(
                    "season_id", "team_id", "pts", "reb", "plus_minus", "ast", "season", "wl", "season_type"
                )
            ))
            teams_info_df = _team_name_lookup()
            average_team_stats_df = TeamStats(team_stats_df, teams_info_df).transform()
            average_team_stats_df = average_team_stats_df.where(pd.notnull(average_team_stats_df), None)
            average_team_stats_dict = average_team_stats_df.to_dict(orient="records")
            return NBADataResponseSchema(success=True, records=average_team_stats_dict)

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching average team stats: {e}")
        return NBADataResponseSchema(success=False, error=str(e))


@router.get("/most_improved_players/season_type={season_type}", response=NBADataResponseSchema)
async def get_most_improved_players(request, season_type: str):

    try:
        def sync_get():
            logger.info("Fetching most improved players from the database...")

            # season_name isn't used to filter here - the comparison needs both the
            # current and previous season's data, so only season_type narrows the query.
            player_stats_df = pd.DataFrame(list(
                FctPlayerStats.objects.filter(season_type=season_type).values("season_id", "player_id", "team_id", "pts", "season", "season_type")
            ))
            players_info_df = _player_name_lookup()
            teams_info_df = _team_name_lookup()
            most_improved_df = MostImprovedPlayers(player_stats_df, players_info_df, teams_info_df).transform()
            most_improved_df = most_improved_df.where(pd.notnull(most_improved_df), None)
            return NBADataResponseSchema(success=True, records=most_improved_df.to_dict(orient="records"))

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching most improved players: {e}")
        return NBADataResponseSchema(success=False, error=str(e))


@router.get("/most_improved_teams/season_type={season_type}", response=NBADataResponseSchema)
async def get_most_improved_teams(request, season_type: str):

    try:
        def sync_get():
            logger.info("Fetching most improved teams from the database...")

            team_stats_df = pd.DataFrame(list(
                FctTeamStats.objects.filter(season_type=season_type).values("season_id", "team_id", "season", "wl", "season_type")
            ))
            teams_info_df = _team_name_lookup()
            most_improved_df = MostImprovedTeams(team_stats_df, teams_info_df).transform()
            most_improved_df = most_improved_df.where(pd.notnull(most_improved_df), None)
            return NBADataResponseSchema(success=True, records=most_improved_df.to_dict(orient="records"))

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching most improved teams: {e}")
        return NBADataResponseSchema(success=False, error=str(e))