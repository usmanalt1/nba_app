LOGISTIC_REGRESSION_MODEL = "logistic_regression_model"
RANDOM_FOREST_MODEL = "random_forest_model"
LAST_RUN = "last_run"


def model_run_cache_key(strategy: str, season: str) -> str:
    return f"{strategy}_{season}_model"
