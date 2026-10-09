"""Which strategy the home page presents, decided from how they have actually called games."""

from typing import List, Optional

from services.ml_model.prediction_history import read_graded


def hit_rate(strategy: str, season: str, season_type: str) -> Optional[float]:
    """Share of graded calls this strategy got right, None until it has one."""
    graded = read_graded(
        strategy=strategy, season=season, season_type=season_type, graded_only=True,
    )
    if not graded:
        return None

    hits = sum(1 for row in graded if row["predicted_home_win"] == row["actual_home_win"])
    return hits / len(graded)


def best_strategy(season: str, season_type: str, candidates: List[str]) -> Optional[str]:
    """The best-performing candidate, None while none of them has a graded call."""
    rated = [
        (strategy, rate)
        for strategy, rate in ((name, hit_rate(name, season, season_type)) for name in candidates)
        if rate is not None
    ]
    if not rated:
        return None

    # max keeps the first of equal rates, so a tie falls to the order candidates came in
    return max(rated, key=lambda pair: pair[1])[0]
