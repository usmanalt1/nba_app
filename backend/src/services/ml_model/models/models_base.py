from abc import ABC, abstractmethod
import pandas as pd

from services.ml_model.models.train_result import TrainResult

class ModelBase(ABC):

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        raise NotImplementedError

    @abstractmethod
    def build(self) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
        raise NotImplementedError

    @abstractmethod
    def train(self) -> TrainResult:
        raise NotImplementedError