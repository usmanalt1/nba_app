from dataclasses import dataclass, field
from typing import Optional

from sklearn.base import BaseEstimator

from services.ml_model.features.transformer_base import TransformerBase

@dataclass
class ModelsConfig:
    target_col: str
    test_filter: int
    transformers: list[TransformerBase] = field(default_factory=list)
    test_size: float = 0.2
    random_state: int = 42
    model: Optional[BaseEstimator] = None