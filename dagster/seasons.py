"""Season naming: a season is named for the year it tips off; months <= September still
belong to the previous one. Matches TransformHelper.create_season_id_year.
"""

from datetime import date


def season_year_for(on: date) -> str:
    """e.g. date(2026, 10, 5) -> "2026-27"."""
    start = on.year if on.month > 9 else on.year - 1
    return f"{start}-{str(start + 1)[2:]}"


def previous_season(season_year: str) -> str:
    """e.g. "2026-27" -> "2025-26"."""
    start = int(season_year.split("-")[0])
    return f"{start - 1}-{str(start)[2:]}"


def current_season(on: date = None) -> str:
    return season_year_for(on or date.today())
