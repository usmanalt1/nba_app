
from typing import TypeVar
from django.db.models import Model
from app.models import FctPlayerStats, DimPlayers
from django.db.models import Avg, Max


M = TypeVar("M", bound=Model)

class Service:
    def __init__(self, model: M):
        self.model: M = model
    
    def get_all(self, limit: str) -> list:
        if self.model is DimPlayers:
            return list(self.model.objects.only("player_id", limit))
        return []
    
    def get_player_stats(self, player_id: str) -> list:
        if self.model is FctPlayerStats:
            player_stats = (self.model.objects
                            .all()
                            .filter(player_id=player_id)
                            .values("season_id")
                            .annotate(
                                average_points = Avg("pts"),
                                average_rebounds = Avg("reb"),
                                average_plus_minus = Avg("plus_minus"),
                                average_assists = Avg("ast"),
                                player_id = Max("player_id")
                            )
            )

            return list(player_stats)
        
        return []
        