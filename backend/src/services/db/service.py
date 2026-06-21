
from typing import TypeVar
from django.db.models import Model

M = TypeVar("M", bound=Model)

class Service:
    def __init__(self, model: M):
        self.model = model
    
    def get_all(self, limit: str):
        return list(self.model.objects.only(limit))