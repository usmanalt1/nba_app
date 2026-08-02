
from typing import TypeVar, Optional
from django.db.models import Model
from app.models import FctPlayerStats, DimPlayers, DimRosters, DimSeasons, DimGames
from django.db.models import Avg, Max
from django.db.models.functions import Round

ROUND = 1
M = TypeVar("M", bound=Model)

class Service:
    def __init__(self, model: M):
        self.model: M = model
    
    def get_all_players(self, season_name = None, team_id = None) -> list:
        if team_id and season_name:
            player_ids = DimRosters.objects.filter(season=str(season_name)).filter(team_id=str(team_id)).values_list("player_id", flat=True)
            return list(self.model.objects.filter(player_id__in=player_ids).only("player_id", "player_name"))

        return list(self.model.objects.only("player_id", "player_name"))
    
    def get_all_seasons(self) -> list:
        return list(self.model.objects.only("season_id", "season_name"))
    
    def get_all_teams(self) -> list:
        return list(self.model.objects.only("team_id", "team_name"))
    
    def get_latest_games(self, season: str) -> list:
        dim_games_model: DimGames = self.model
        latest_date = (
            dim_games_model.objects.filter(season=season)
            .order_by("-game_date")
            .values_list("game_date", flat=True)
            .first()
        )
        if latest_date is None:
            return []

        return list(
            dim_games_model.objects.filter(season=season, game_date=latest_date)
            .only("game_date", "season", "home_team_name", "away_team_name", "home_pts", "away_pts")
        )

    def get_all_player_stats(self, season_id: Optional[int] = None) -> list:
        queryset = FctPlayerStats.objects.select_related("player").values("player_id", "season_id", "pts", "reb", "plus_minus", "ast", "player__player_name")
        if season_id is not None:
            queryset = queryset.filter(season_id=str(season_id))
        return list(queryset)
    
    def get_player_stats(self, player_id: Optional[str] = None, season_id: Optional[int] = None) -> list:
        qs = FctPlayerStats.objects.select_related("player")
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
        