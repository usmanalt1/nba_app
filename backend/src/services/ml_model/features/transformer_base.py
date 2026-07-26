from abc import ABC, abstractmethod
import pandas as pd

class TransformerBase(ABC):
    @abstractmethod
    def transform(self) -> pd.DataFrame:
        raise NotImplementedError