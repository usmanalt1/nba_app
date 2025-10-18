from data.collect import CollectRawNBAData
import pandas as pd
import logging
from datetime import datetime, timedelta
import argparse
from data.data_models import SeasonRecord, TeamInfo, TeamRoster, PlayerInfo, TeamStats, PlayerStats
from data.db_service import DBService

logging.basicConfig(level=logging.INFO)
DB_URL = """mysql+pymysql://admin:admin@mysql-host:3307/nba_test"""

def main() -> pd.DataFrame:
    date = (datetime.today() - timedelta(weeks=52))
    parser = argparse.ArgumentParser(description="NBA Data Collection and Analytics")
    parser.add_argument("--date", default=date,
                    help='Date in the format YYYY-MM-DD (default: today\'s date)')
    parser.add_argument("--run-db", default=False)
    
    args = parser.parse_args()
    raw_tables = CollectRawNBAData(date_to_run=args.date).gather_and_import_nba_data()
    logging.info("...Raw Data Collected from NBA API")
    if args.run_db:
        db_service = DBService(DB_URL)
        table_model_map = {
            "season_record": SeasonRecord,
            "teams_info": TeamInfo,
            "players_info": PlayerInfo,
            "teams_roster": TeamRoster,
            "team_stats": TeamStats,
            "player_stats": PlayerStats,
        }

        for table_name, model in table_model_map.items():
            db_service.create_if_not_exists()
            table_df_as_dict = raw_tables.get(table_name).to_dict(orient="records")
            if table_name in ["season_record", "teams_info", "players_info", "teams_roster"]:
                db_service._insert_if_not_exists(model=model, 
                                                 records=table_df_as_dict, 
                                                 unique_field="season_id")
            elif table_name in ["team_stats"]:
                db_service._insert_if_not_exists(model=model, 
                                                 records=table_df_as_dict, 
                                                 unique_field="date", 
                                                 secondary_unique_field="team_id")
            else:
                db_service._insert_if_not_exists(model=model, 
                                                 records=table_df_as_dict, 
                                                 unique_field="date", 
                                                 secondary_unique_field="player_id")

        logging.info("...Data Upserted into Database")

    # init_s3 = S3Helper(args.date)
    # init_s3.save_tables_from_dict(raw_tables, "nba-analytics-ma")

if __name__ == "__main__":
    main()