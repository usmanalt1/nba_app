# api.py
from ninja import Router
from app.models import PlayerStats
from typing import List
from data.collect import CollectRawNBAData
from app.models import SeasonRecord, TeamInfo, PlayerInfo, TeamRoster, TeamStats, PlayerStats
from datetime import datetime, timedelta
from ninja import NinjaAPI
import logging
logger = logging.getLogger(__name__)

router = Router()

api = NinjaAPI()
api.add_router("/nba/", router)

@router.get("/collect-and-upsert/")
def collect_and_upsert(request):
    date = datetime.today() - timedelta(weeks=52)
    raw_tables = CollectRawNBAData(date_to_run=date).gather_and_import_nba_data()
    table_model_map = {
        "season_record": SeasonRecord,
        "teams_info": TeamInfo,
        "players_info": PlayerInfo,
        "teams_roster": TeamRoster,
        "team_stats": TeamStats,
        "player_stats": PlayerStats,
    }

    for table_name, model in table_model_map.items():
        df = raw_tables.get(table_name)
        if df is not None:
            logger.info(f"Upserting data for table: {table_name}")
            columns = df.columns
            logger.info(f"columns: {columns}")
            records = df.to_dict(orient="records")
            for record in records:
                if table_name == "season_record":
                    model.objects.update_or_create(
                        season_id=record["season_id"],
                        defaults=record
                    )
                elif table_name == "team_info":
                    model.objects.update_or_create(
                        season_id=record["season_id"],
                        abbreviation=record["abbreviation"],
                        defaults=record
                    )
                elif table_name == "team_stats":
                    model.objects.update_or_create(
                        date=record["date"],
                        team_id=record["team_id"],
                        defaults=record
                    )
                elif table_name == "player_stats": 
                    model.objects.update_or_create(
                        date=record["date"],
                        player_id=record["player_id"],
                        defaults=record
                    )
                elif table_name == "players_info":
                    model.objects.update_or_create(
                        season_id=record["season_id"],
                        full_name=record["full_name"],
                        defaults=record
                    )
                elif table_name == "teams_roster":
                    model.objects.update_or_create(
                        team_id=record["team_id"],
                        player_id=record["player_id"],
                        season_id=record["season_id"],
                        defaults=record
                    )
    return {"success": True}