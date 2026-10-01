
from typing import TypeVar, Optional
from django.db.models import Model
from app.models import FctPlayerStats, FctTeamStats, DimPlayers, DimRosters, DimSeasons, DimGames, DimTeams
from django.db.models import Avg, Count, ExpressionWrapper, FloatField, Max, Q, Sum, Value
from django.db.models.functions import NullIf, Round

ROUND = 1
M = TypeVar("M", bound=Model)


def _shooting_pct(made: str, attempted: str):
    """Season shooting percentage, computed from totals rather than per-game ratios.

    Averaging each game's fg_pct would weight a 1-for-1 night the same as a
    12-for-20 night. NullIf keeps a player with zero attempts from dividing by zero
    (the result is NULL instead).
    """
    return Round(
        ExpressionWrapper(
            Sum(made) * Value(100.0) / NullIf(Sum(attempted), Value(0.0)),
            output_field=FloatField(),
        ),
        ROUND,
    )


def _box_score_averages() -> dict:
    """Per-game averages for every stat on the box-score fact tables."""
    return dict(
        average_minutes=Round(Avg("min"), ROUND),
        average_points=Round(Avg("pts"), ROUND),
        average_field_goals_made=Round(Avg("fgm"), ROUND),
        average_field_goals_attempted=Round(Avg("fga"), ROUND),
        average_three_pointers_made=Round(Avg("fg3m"), ROUND),
        average_three_pointers_attempted=Round(Avg("fg3a"), ROUND),
        average_free_throws_made=Round(Avg("ftm"), ROUND),
        average_free_throws_attempted=Round(Avg("fta"), ROUND),
        average_offensive_rebounds=Round(Avg("oreb"), ROUND),
        average_defensive_rebounds=Round(Avg("dreb"), ROUND),
        average_rebounds=Round(Avg("reb"), ROUND),
        average_assists=Round(Avg("ast"), ROUND),
        average_steals=Round(Avg("stl"), ROUND),
        average_blocks=Round(Avg("blk"), ROUND),
        average_turnovers=Round(Avg("tov"), ROUND),
        average_fouls=Round(Avg("pf"), ROUND),
        average_plus_minus=Round(Avg("plus_minus"), ROUND),
        field_goal_pct=_shooting_pct("fgm", "fga"),
        three_point_pct=_shooting_pct("fg3m", "fg3a"),
        free_throw_pct=_shooting_pct("ftm", "fta"),
    )

class Service:
    def __init__(self, model: M):
        self.model: M = model
    
    def get_all_players(self, season_name = None, team_id = None) -> list:
        if team_id and season_name:
            player_ids = DimRosters.objects.filter(season=str(season_name)).filter(team_id=str(team_id)).values_list("player_id", flat=True)
            return list(self.model.objects.filter(player_id__in=player_ids).only("player_id", "player_name"))

        if team_id:
            player_ids = DimRosters.objects.filter(team_id=str(team_id)).values_list("player_id", flat=True)
            return list(self.model.objects.filter(player_id__in=player_ids).only("player_id", "player_name"))

        if season_name:
            player_ids = DimRosters.objects.filter(season=str(season_name)).values_list("player_id", flat=True)
            return list(self.model.objects.filter(player_id__in=player_ids).only("player_id", "player_name"))
        
        return list(self.model.objects.only("player_id", "player_name"))
    
    def get_seasons_with_stats(self) -> list:
        """Seasons that have recorded games, newest last.

        dim_seasons carries upcoming seasons too (e.g. 2026-27 before tip-off),
        which would otherwise offer the user a season with an empty table.
        """
        played = set(FctPlayerStats.objects.values_list("season", flat=True).distinct())
        seasons = [s for s in DimSeasons.objects.all() if s.season_name in played]
        return sorted(seasons, key=lambda s: s.season_name or "")

    def get_all_seasons(self) -> list:
        return list(self.model.objects.only("season_id", "season_name"))
    
    def get_all_teams(self) -> list:
        return list(self.model.objects.only("team_id", "team_name"))
    
    def get_latest_games(self, season: str, season_type: str) -> list:
        dim_games_model: DimGames = self.model
        latest_date = (
            dim_games_model.objects.filter(season=season, season_type=season_type)
            .order_by("-game_date")
            .values_list("game_date", flat=True)
            .distinct()[:5]
        )
        if not latest_date:
            return []

        return list(
            dim_games_model.objects.filter(season=season, season_type=season_type, game_date__in=latest_date)
            .only("game_date", "season", "home_team_name", "away_team_name", "home_pts", "away_pts")
        )

    def get_all_player_stats(self, season_id: Optional[int] = None) -> list:
        queryset = FctPlayerStats.objects.select_related("player").values("player_id", "season_id", "pts", "reb", "plus_minus", "ast", "player__player_name")
        if season_id is not None:
            queryset = queryset.filter(season_id=str(season_id))
        return list(queryset)
    
    def get_season_player_stats(
        self,
        season_name: str,
        team_id: Optional[int] = None,
        position: Optional[str] = None,
        season_type: str = "regular",
    ) -> list:
        """Per-game averages for every player in a season, one row per player.

        season_type is 'regular' or 'playoffs'. fct_player_stats holds both, so
        leaving it out averages playoff games into the regular-season numbers.
        """
        qs = FctPlayerStats.objects.select_related("player").filter(
            season=str(season_name), season_type=season_type,
        )
        if team_id:
            qs = qs.filter(team_id=team_id)
        if position:
            qs = qs.filter(player__position__icontains=position)

        return list(
            qs.values("player_id", "season")
            .annotate(
                games_played=Count("game_id", distinct=True),
                player_name=Max("player__player_name"),
                position=Max("player__position"),
                **_box_score_averages(),
            )
            .order_by("-average_points")
        )

    def get_season_team_stats(
        self,
        season_name: str,
        team_id: Optional[int] = None,
        season_type: str = "regular",
    ) -> list:
        """Per-game averages and win/loss record for each team in a season."""
        qs = FctTeamStats.objects.filter(season=str(season_name), season_type=season_type)
        if team_id:
            qs = qs.filter(team_id=team_id)

        rows = list(
            qs.values("team_id", "season")
            .annotate(
                games_played=Count("game_id", distinct=True),
                wins=Count("game_id", filter=Q(wl="W"), distinct=True),
                losses=Count("game_id", filter=Q(wl="L"), distinct=True),
                **_box_score_averages(),
            )
            .order_by("-wins")
        )
        # fct_team_stats has no FK to dim_teams, so attach names from one lookup.
        names = dict(DimTeams.objects.values_list("team_id", "team_name"))
        for row in rows:
            row["team_name"] = names.get(row["team_id"], str(row["team_id"]))
        return rows

    def get_player_stats(
        self,
        player_id: Optional[str] = None,
        season_id: Optional[int] = None,
        season_type: str = "regular",
    ) -> list:
        """Per-game averages grouped by season.

        season_type is 'regular' or 'playoffs'; pass None for both combined.
        """
        qs = FctPlayerStats.objects.select_related("player")
        if season_type:
            qs = qs.filter(season_type=season_type)
        if player_id:
            qs = qs.filter(player_id=player_id)
        if season_id:
            qs = qs.filter(season=str(season_id))

        if player_id:
            group_fields = ["season_id"]
        else:
            group_fields = ["player_id", "season_id", "season", "player__player_name"]

        player_stats = qs.values(*group_fields).annotate(
            average_points=Round(Avg("pts"), ROUND),
            average_rebounds=Round(Avg("reb"), ROUND),
            average_plus_minus=Round(Avg("plus_minus"), ROUND),
            average_assists=Round(Avg("ast"), ROUND),
        )
        if player_id:
            player_stats = player_stats.annotate(player_id=Round(Max("player_id"), ROUND))
        
        player_stats = player_stats.annotate(player_name=Max("player__player_name"))
        return list(player_stats)
