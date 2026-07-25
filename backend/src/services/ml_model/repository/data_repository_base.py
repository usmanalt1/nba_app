from abc import ABC, abstractmethod
import pandas as pd

class DataRepositoryBase(ABC):
    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass