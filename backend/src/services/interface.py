from abc import ABC, abstractmethod
import pandas as pd

class StorageBase(ABC):
    @abstractmethod
    def save(self, df: pd.DataFrame, file_name: str, season: str, run_timestamp: str) -> None:
        pass

    @abstractmethod
    def read(self, latest_run_id: str, seasons: list, table: str) -> pd.DataFrame:
        pass