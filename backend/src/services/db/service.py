
from typing import TypeVar
from django.db.models import Model
from app.models import FctPlayerStats, DimPlayers, DimRosters, DimSeasons
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
    
    def get_player_stats(self, player_id: str) -> list:
        if self.model is FctPlayerStats:
            player_stats = (self.model.objects
                            .all()
                            .filter(player_id=player_id)
                            .values("season_id")
                            .annotate(
                                average_points = Round(Avg("pts"), ROUND),
                                average_rebounds = Round(Avg("reb"), ROUND),
                                average_plus_minus = Round(Avg("plus_minus"), ROUND),
                                average_assists = Round(Avg("ast"), ROUND),
                                player_id = Round(Max("player_id"), ROUND)
                            )
            )

            return list(player_stats)
        
        return []
        