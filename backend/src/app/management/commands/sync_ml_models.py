from django.core.management.base import BaseCommand

from app.models import MlModels
from services.ml_model.models.models_strategy import STRATEGY_REGISTRY


class Command(BaseCommand):
    help = "Sync the MlModels lookup table with STRATEGY_REGISTRY's current keys"

    def handle(self, *args, **options):
        for name in STRATEGY_REGISTRY:
            _, created = MlModels.objects.get_or_create(model_name=name)
            if created:
                self.stdout.write(f"Added: {name}")

        self.stdout.write(self.style.SUCCESS("MlModels sync complete"))
