from logging import getLogger
from app.models import SeasonRecord, TeamInfo, PlayerInfo, TeamRoster, TeamStats, PlayerStats, TeamMatchups
import pandas as pd

logger = getLogger(__name__)
class DBOperations:
    def __init__(self):
        self.table_model_map = {
            "season_record": SeasonRecord,
            "teams_info": TeamInfo,
            "players_info": PlayerInfo,
            "teams_roster": TeamRoster,
            "team_stats": TeamStats,
            "player_stats": PlayerStats,
            "team_matchups": TeamMatchups,
        }
    
    def upsert_nba_data(self, raw_tables: dict, get_table_name: str = None) -> None:
        logger.info("Starting upsert of NBA data into the database")
        if get_table_name:
            self.table_model_map = {
                get_table_name: self.table_model_map.get(get_table_name)}
        try:
            for table_name, model in self.table_model_map.items():
                df = raw_tables.get(table_name)
                logger.info(f"Upserting data for table: {table_name}, Number of records: {len(df) if df is not None else 0}")
                if not df.empty:
                    logger.info(f"Upserting data for table: {table_name}")
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
                        elif table_name == "team_matchups":
                            model.objects.update_or_create(
                                season_id=record["season_id"],
                                team_id=record["team_id"],
                                game_date=record["game_date"],
                                defaults=record
                            )
        except Exception as e:
            logger.error(f"Error during upsert operation: {e}")
            raise
    