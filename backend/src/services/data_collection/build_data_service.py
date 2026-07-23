
from services.data_collection.collect import CollectRawNBAData
from services.object_storage.service import ObjectStorageService
from datetime import datetime, timedelta
from django.utils import timezone
from app.models import PlayerAwards
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class BuildDataService:
    def __init__(self, date = None):
        self.date = date or datetime.today() - timedelta(weeks=52)

    def build_nba_data(self, table_name = None, season_id: str = None, season_year: str = None, team_roster: bool = False) -> dict:
        raw_tables = CollectRawNBAData(date_to_run=self.date).gather_and_import_nba_data(table_name=table_name, season_id=season_id, season_year=season_year, team_roster=team_roster)

        return raw_tables

    def build_player_awards(self, players_table: pd.DataFrame) -> dict:
        """Fetch player awards, skipping players already stored, and save the result
        to object storage - same collect -> object storage -> /load_to_postgres flow
        every other table in this pipeline uses.

        Awards are static history - once a player has rows in player_awards there's
        no need to hit the (slow, rate-limited) nba_api endpoint for them again.
        """
        existing_player_ids = set(PlayerAwards.objects.values_list("player_id", flat=True).distinct())
        players_to_fetch = players_table[~players_table["player_id"].isin(existing_player_ids)]

        logger.info(
            f"{len(existing_player_ids)} players already have awards data; "
            f"fetching {len(players_to_fetch)} of {len(players_table)} total players"
        )

        if players_to_fetch.empty:
            return {"fetched": 0, "saved": 0, "skipped": len(players_table)}

        collector = CollectRawNBAData(date_to_run=self.date)
        df_awards = collector._get_player_awards(df_players=players_to_fetch)

        saved = 0
        if not df_awards.empty:
            # the raw nba_api response includes columns the model deliberately doesn't store
            # (e.g. "type", which is always the literal string "Award") - keep only real fields
            model_fields = {f.name for f in PlayerAwards._meta.get_fields() if f.concrete and f.name != "id"}
            df_awards = df_awards[[c for c in df_awards.columns if c in model_fields]]
            df_awards["run_timestamp"] = timezone.now()

            object_storage_service = ObjectStorageService().get_storage()
            object_storage_service.save(df=df_awards, file_name="player_awards", season=collector.season_year)
            saved = len(df_awards)

        return {"fetched": len(players_to_fetch), "saved": saved, "skipped": len(existing_player_ids)}
