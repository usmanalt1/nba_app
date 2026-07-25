from services.ml_model.repository.data_repository_base import DataRepositoryBase
from services.db.db_service import DBService
import pandas as pd

class PostgresRepository(DataRepositoryBase):
    def __init__(self):
        self.db_service = DBService()
    
    def load(self, table_name: str) -> pd.DataFrame:
        return self.db_service.read(table_name)