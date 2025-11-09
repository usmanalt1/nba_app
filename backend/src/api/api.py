# api.py
from ninja import Router
from ninja import Schema
from ninja import NinjaAPI
import logging
from services.data_collection.build_data_service import BuildDataService
from services.db.db_service import DBService
from typing import Optional, Dict, Any, List
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

router = Router()

api = NinjaAPI()
api.add_router("/nba/", router)

class NBADataResponseSchema(Schema):
    success: bool
    error: Optional[str] = None
    records: Optional[List[Dict[str, Any]]] = None

@router.get("/collect/all", response=NBADataResponseSchema)
async def collect_all(request):
    try:
        def sync_collect_and_upsert():
            raw_tables = BuildDataService().build_nba_data()
            logger.info("Raw NBA data collected successfully.")
            
            db_operations = DBService()
            db_operations.upsert_nba_data(raw_tables)
            logger.info("NBA data upserted to the database successfully.")

        await sync_to_async(sync_collect_and_upsert)()
            
    except Exception as e:
        logger.error(f"Error during data collection and upsert: {e}")
        return NBADataResponseSchema(success=False, error=str(e))
    
    return NBADataResponseSchema(success=True)

@router.get("/collect/{table_name}", response=NBADataResponseSchema)
async def collect_data_by_table(request, table_name: str):
    try:
        def sync_collect():
            raw_tables = BuildDataService().build_nba_data(table_name=table_name)
            logger.info(f"Raw NBA data for table {table_name} collected successfully.")
            
            db_operations = DBService()
            db_operations.upsert_nba_data(raw_tables, get_table_name=table_name)
            logger.info(f"NBA data for table {table_name} upserted to the database successfully.")
        await sync_to_async(sync_collect)()
        
    except Exception as e:
        logger.error(f"Error during data collection and upsert for table {table_name}: {e}")
        return NBADataResponseSchema(success=False, error=str(e))
    
    return NBADataResponseSchema(success=True)

@router.get("/collect/season/{season_year}", response=NBADataResponseSchema)
async def collect_data_by_season(request, season_year: str):
        try:
            #season_year format "2022-23"
            #TODO validate season_year format
            split_year = season_year.split("-")
            season_id = f"{split_year[0][-2:]}0{split_year[1][-2:]}"
            def sync_collect_and_upsert_for_date():
                raw_tables = BuildDataService().build_nba_data(season_id=season_id, season_year=season_year)
                logger.info(f"Raw NBA data for table collected successfully.")
                
                db_operations = DBService()
                db_operations.upsert_nba_data(raw_tables)

            await sync_to_async(sync_collect_and_upsert_for_date)()
        except Exception as e:
            logger.error(f"Error during data collection and upsert: {e}")
            return NBADataResponseSchema(success=False, error=str(e))
        
        return NBADataResponseSchema(success=True)

@router.get("/collect/season/{table_name}/{season_year}", response=NBADataResponseSchema)
async def collect_data_by_table_season(request, table_name: str, season_year: str):
    try:
        def sync_collect():
            split_year = season_year.split("-")
            season_id = f"{split_year[0][-2:]}0{split_year[1][-2:]}"
            raw_tables = BuildDataService().build_nba_data(table_name=table_name, season_id=season_id, season_year=season_year)
            logger.info(f"Raw NBA data for table {table_name} collected successfully.")
            
            db_operations = DBService()
            db_operations.upsert_nba_data(raw_tables=raw_tables, get_table_name=table_name)
            logger.info(f"NBA data for table {table_name} upserted to the database successfully.")
        await sync_to_async(sync_collect)()
        
    except Exception as e:
        logger.error(f"Error during data collection and upsert for table {table_name}: {e}")
        return NBADataResponseSchema(success=False, error=str(e))
    
    return NBADataResponseSchema(success=True)

@router.get("/stats/{table_name}")
async def get_table_data(request, table_name: str):
    try:
        def sync_get_data():
            db_operations = DBService()
            records = db_operations.get_table_data(table_name)
            return records

        records = await sync_to_async(sync_get_data)()
    except Exception as e:
        logger.error(f"Error retrieving data for table {table_name}: {e}")
        return NBADataResponseSchema(success=False, error=str(e))
    
    return NBADataResponseSchema(success=True, records=records)

@router.get("/model/run")
async def run_model(request):
    try:
        from services.predictive_model.service import PredictiveModelService

        def sync_run_model():
            predictive_model_service = PredictiveModelService()
            classification_report = predictive_model_service.run()
            return classification_report

        classification_report = await sync_to_async(sync_run_model)()
        return NBADataResponseSchema(success=True)
    except Exception as e:
        logger.error(f"Error running predictive model: {e}")
        return NBADataResponseSchema(success=False, error=str(e))

