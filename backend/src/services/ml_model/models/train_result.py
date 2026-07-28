from dataclasses import dataclass

import pandas as pd
from sklearn.base import BaseEstimator


@dataclass
class TrainResult:
    model: BaseEstimator
    metrics: dict[str, float]
    predictions: pd.DataFrame
    season_record: pd.DataFrame = pd.DataFrame()
