LOGISTIC_REGRESSION_MODEL = "logistic_regression_model"
RANDOM_FOREST_MODEL = "random_forest_model"
LAST_RUN = "last_run"
TEAM_COLOURS = "team_colours"


def model_run_cache_key(strategy: str, season: str) -> str:
    return f"{strategy}_{season}_model"


def hot_and_cold_cache_key(season: str, season_type: str, limit: int) -> str:
    """`season` is the requested one, so a cached entry covers the season resolution too."""
    return f"hot_and_cold_{season}_{season_type}_{limit}"
