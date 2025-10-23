# api.py
from ninja import Router
from ninja import Schema
from ninja import NinjaAPI
import logging
from services.build_data_service import BuildDataService
from services.db.db_operations import DBOperations
from typing import Optional
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

router = Router()

api = NinjaAPI()
api.add_router("/nba/", router)

class NBADataResponseSchema(Schema):
    success: bool
    error: Optional[str] = None

@router.get("/collect_all", response=NBADataResponseSchema)
async def collect_and_upsert(request):
    try:
        def sync_collect_and_upsert():
            raw_tables = BuildDataService().build_nba_data()
            logger.info("Raw NBA data collected successfully.")
            
            db_operations = DBOperations()
            db_operations.upsert_nba_data(raw_tables)
            logger.info("NBA data upserted to the database successfully.")

        await sync_to_async(sync_collect_and_upsert)()
            
    except Exception as e:
        logger.error(f"Error during data collection and upsert: {e}")
        return NBADataResponseSchema(success=False, error=str(e))
    
    return NBADataResponseSchema(success=True)

@router.get("/collect/{table_name}", response=NBADataResponseSchema)
async def collect_table_data(request, table_name: str):
    try:
        def sync_collect():
            raw_tables = BuildDataService().build_nba_data(table_name=table_name)
            logger.info(f"Raw NBA data for table {table_name} collected successfully.")
            
            db_operations = DBOperations()
            db_operations.upsert_nba_data(raw_tables, get_table_name=table_name)
            logger.info(f"NBA data for table {table_name} upserted to the database successfully.")
        await sync_to_async(sync_collect)()
        
    except Exception as e:
        logger.error(f"Error during data collection and upsert for table {table_name}: {e}")
        return NBADataResponseSchema(success=False, error=str(e))
    
    return NBADataResponseSchema(success=True)