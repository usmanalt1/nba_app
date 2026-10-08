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
from app.models import (
    DimPlayers, FctPlayerStats, DimSeasons, DimTeams, DimGames, DimRosters, FctTeamStats,
    MartPlayerGameForm, MartTeamGameForm,
)
from django.db.models import Count
from services.redis.redis_client import RedisClient
from services.redis.redis_key_constants import hot_and_cold_cache_key
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


def _player_team_lookup() -> pd.DataFrame:
    """The team each player finished a given season with, keyed on (player_id, season)."""
    df = pd.DataFrame(list(
        DimRosters.objects
        .exclude(last_game_with_team__isnull=True)
        .values("player_id", "season", "team_id", "last_game_with_team")
        .order_by("last_game_with_team")
    ))
    if df.empty:
        return pd.DataFrame(columns=["player_id", "season", "team_id"])

    # One row per roster stint, so the last one a player appears in is the team they
    # ended the season on. Nulls are excluded above because Postgres sorts them last,
    # which would otherwise hand the win to a row with no date.
    latest = df.drop_duplicates(subset=["player_id", "season"], keep="last")
    # dim_rosters.team_id is declared CharField over an integer column, so pin the dtype
    # rather than let the merge key depend on which the driver hands back.
    return latest.assign(team_id=latest["team_id"].astype(int))[["player_id", "season", "team_id"]]


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
async def get_average_player_stats(request, season_name: str, season_type: str, min_games: int = 0):

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
            average_player_stats_df = PlayerStats(
                player_stats_df, players_info_df, teams_info_df, _player_team_lookup(),
                min_games=min_games,
            ).transform()
            average_player_stats_df = average_player_stats_df.where(pd.notnull(average_player_stats_df), None)
            average_players_stats_dict = average_player_stats_df.to_dict(orient="records")
            return NBADataResponseSchema(success=True, records=average_players_stats_dict)

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching average player stats: {e}")
        return NBADataResponseSchema(success=False, error=str(e))


@router.get("/average_team_stats/season={season_name}/season_type={season_type}", response=NBADataResponseSchema)
async def get_average_team_stats(request, season_name: str, season_type: str, min_games: int = 0):

    try:
        def sync_get():
            logger.info("Fetching average team stats from the database...")

            team_stats_df = pd.DataFrame(list(
                FctTeamStats.objects.filter(season=season_name, season_type=season_type).values(
                    "season_id", "team_id", "pts", "reb", "plus_minus", "ast", "season", "wl", "season_type"
                )
            ))
            teams_info_df = _team_name_lookup()
            average_team_stats_df = TeamStats(team_stats_df, teams_info_df, min_games=min_games).transform()
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
            most_improved_df = MostImprovedPlayers(
                player_stats_df, players_info_df, teams_info_df, _player_team_lookup(),
            ).transform()
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

# A last-10 window only means something once there are enough earlier games to compare
# it against; worm-analytics sets the floor at 20 season games.
MIN_FORM_GAMES = 20
# Under this many qualifying players a season hasn't really started, so serve the
# previous one and let the caller label it.
MIN_QUALIFIED_PLAYERS = 20
HOT_AND_COLD_LIMIT_DEFAULT = 5
HOT_AND_COLD_LIMIT_MAX = 10
# The marts only change when the pipeline runs. There is no dbt post-hook to invalidate
# this, so it expires on its own and refresh=true forces a reread after a build.
HOT_AND_COLD_CACHE_TTL_SECONDS = 6 * 60 * 60


class HotColdResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None
    # The season actually served, which is not always the newest one on record.
    season: Optional[str] = None
    latest_season: Optional[str] = None
    season_is_fallback: bool = False
    min_games: int = MIN_FORM_GAMES


def _round(value, digits: int = 1):
    """float() first: the win-percentage columns are SQL numeric, so they arrive as
    Decimal and would serialise to JSON as a quoted string."""
    return None if value is None else round(float(value), digits)


def _resolve_form_season(season_type: str, requested: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """The newest season with enough qualifying players, and the newest on record."""
    latest = (
        MartPlayerGameForm.objects.filter(season_type=season_type)
        .order_by("-season").values_list("season", flat=True).first()
    )
    if requested:
        return requested, latest

    by_season = (
        MartPlayerGameForm.objects
        .filter(season_type=season_type, is_latest=True, games_in_season__gte=MIN_FORM_GAMES)
        .values("season")
        .annotate(qualified=Count("player_id"))
        .filter(qualified__gte=MIN_QUALIFIED_PLAYERS)
        .order_by("-season")
    )
    rows = list(by_season[:1])
    return (rows[0]["season"] if rows else None), latest


def _extremes(queryset, order_field: str, limit: int, key: str) -> list:
    """Top `limit` by descending then ascending `order_field`, without repeating an
    entity when few enough qualify that the two ends would overlap."""
    hot = list(queryset.order_by(f"-{order_field}")[:limit])
    cold = list(queryset.order_by(order_field)[:limit])
    seen = {row[key] for row in hot}
    return hot + [row for row in reversed(cold) if row[key] not in seen]


def _player_form_rows(season: str, season_type: str, limit: int) -> list:
    qs = (
        MartPlayerGameForm.objects
        .filter(
            season=season, season_type=season_type, is_latest=True,
            games_in_season__gte=MIN_FORM_GAMES, delta_pts__isnull=False,
        )
        .values(
            "player_id", "player_name", "team_id", "games_in_season",
            "form_pts", "base_pts", "delta_pts", "form_ts_pct", "delta_ts_pct",
        )
    )
    return [
        {
            "scope": "player",
            "entity_id": row["player_id"],
            "name": row["player_name"],
            "team_id": row["team_id"],
            "games": row["games_in_season"],
            "form": _round(row["form_pts"]),
            "baseline": _round(row["base_pts"]),
            "delta": _round(row["delta_pts"]),
            "form_ts_pct": _round(row["form_ts_pct"]),
            "delta_ts_pct": _round(row["delta_ts_pct"]),
        }
        for row in _extremes(qs, "delta_pts", limit, "player_id")
    ]


def _team_form_rows(season: str, season_type: str, limit: int) -> list:
    qs = (
        MartTeamGameForm.objects
        .filter(
            season=season, season_type=season_type, is_latest=True,
            games_in_season__gte=MIN_FORM_GAMES, delta_margin__isnull=False,
        )
        .values(
            "team_id", "games_in_season", "form_margin", "base_margin",
            "delta_margin", "form_wins", "form_games", "delta_win_pct",
        )
    )
    names_df = _team_name_lookup()
    names = dict(zip(names_df["team_id"], names_df["team_name"]))
    return [
        {
            "scope": "team",
            "entity_id": row["team_id"],
            "name": names.get(row["team_id"], str(row["team_id"])),
            "team_id": row["team_id"],
            "games": row["games_in_season"],
            "form": _round(row["form_margin"]),
            "baseline": _round(row["base_margin"]),
            "delta": _round(row["delta_margin"]),
            "form_wins": row["form_wins"],
            "form_games": row["form_games"],
            "delta_win_pct": _round(row["delta_win_pct"]),
        }
        for row in _extremes(qs, "delta_margin", limit, "team_id")
    ]


@router.get("/hot_and_cold", response=HotColdResponseSchema)
async def get_hot_and_cold(
    request,
    season_type: str = "regular",
    season: Optional[str] = None,
    limit: int = HOT_AND_COLD_LIMIT_DEFAULT,
    refresh: bool = False,
):
    """Players and teams whose last 10 games differ most from the rest of their season.

    Serves the newest season that has enough games to measure; season_is_fallback says
    whether that is the newest season on record.
    """
    capped = max(1, min(limit, HOT_AND_COLD_LIMIT_MAX))
    cache_key = hot_and_cold_cache_key(season or "auto", season_type, capped)

    try:
        def sync_get():
            cache = RedisClient()
            if not refresh:
                try:
                    cached = cache.get(cache_key)
                    if cached:
                        return HotColdResponseSchema(**cached)
                except Exception:
                    logger.exception("hot_and_cold cache read failed, reading from the DB")

            resolved, latest = _resolve_form_season(season_type, season)
            if resolved is None:
                # No season has enough games yet. An empty records list with the season
                # context is what lets the UI explain itself instead of going blank.
                return HotColdResponseSchema(
                    success=True, records=[], season=None, latest_season=latest,
                    season_is_fallback=False, min_games=MIN_FORM_GAMES,
                )

            payload = {
                "success": True,
                "records": _player_form_rows(resolved, season_type, capped)
                           + _team_form_rows(resolved, season_type, capped),
                "season": resolved,
                "latest_season": latest,
                "season_is_fallback": bool(latest and resolved != latest),
                "min_games": MIN_FORM_GAMES,
            }
            try:
                cache.set(cache_key, payload, ex=HOT_AND_COLD_CACHE_TTL_SECONDS)
            except Exception:
                logger.exception("hot_and_cold cache write failed")
            return HotColdResponseSchema(**payload)

        return await asyncio.to_thread(sync_get)
    except Exception as e:
        logger.error(f"Error fetching hot and cold: {e}")
        return HotColdResponseSchema(success=False, error=str(e))
