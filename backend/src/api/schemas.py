from typing import Optional
from ninja import Schema

class SeasonRecord(Schema):
    id: Optional[int] = None
    season_id: int

class TeamInfo(Schema):
    id: Optional[int] = None
    season_id: int
    abbreviation: str
    nickname: str
    city: str
    state: str
    year_founded: int
    full_name: str

class PlayerInfo(Schema):
    id: Optional[int] = None
    season_id: int
    full_name: str
    first_name: str
    last_name: str
    is_active: bool

class TeamRoster(Schema):
    id: Optional[int] = None
    team_id: int
    player_id: int
    season_id: int
    player: str
    age: Optional[int] = None
    position: Optional[str] = None

class PlayerStats(Schema):
    id: Optional[int] = None
    player_id: int
    season_id: int
    team_id: int
    rank: int
    player: str
    team: str
    gp: int
    min: float
    fgm: float
    fga: float
    fg_pct: float
    fg3m: float
    fg3a: float
    fg3_pct: float
    ftm: float
    fta: float
    ft_pct: float
    oreb: float
    dreb: float
    reb: float
    ast: float
    stl: float
    blk: float
    tov: float
    pf: float
    pts: float
    eff: float
    ast_tov: float
    stl_tov: float
    date: str

class TeamStats(Schema):
    id: Optional[int] = None
    group_value: str
    season_id: int
    team_id: int
    season_year: str
    gp: int
    w: int
    l: int
    w_pct: float
    min: float
    fgm: float
    fga: float
    fg_pct: float
    fg3m: float
    fg3a: float
    fg3_pct: float
    ftm: float
    fta: float
    ft_pct: float
    oreb: float
    dreb: float
    reb: float
    ast: float
    tov: float
    stl: float
    blk: float
    blka: float
    pf: float
    pfd: float
    pts: float
    plus_minus: float
    gp_rank: int
    w_rank: int
    l_rank: int
    w_pct_rank: int
    min_rank: int
    fgm_rank: int
    fga_rank: int
    fg_pct_rank: int
    fg3m_rank: int
    fg3a_rank: int
    fg3_pct_rank: int
    ftm_rank: int
    fta_rank: int
    ft_pct_rank: int
    oreb_rank: int
    dreb_rank: int
    reb_rank: int
    ast_rank: int
    tov_rank: int
    stl_rank: int
    blk_rank: int
    blka_rank: int
    pf_rank: int
    pfd_rank: int
    pts_rank: int
    plus_minus_rank: int
    date: str

class TeamMatchups(Schema):
    id: Optional[int] = None
    season_id: str
    team_id: int
    team_abbreviation: str
    team_name: str
    game_id: str
    game_date: str  # ISO format date string
    matchup: str
    wl: str
    min: int
    pts: int
    fgm: int
    fga: int
    fg_pct: float
    fg3m: int
    fg3a: int
    fg3_pct: float
    ftm: int
    fta: int
    ft_pct: float
    oreb: int
    dreb: int
    reb: int
    ast: int
    stl: int
    blk: int
    tov: int
    pf: int
    plus_minus: float

class PlayerStatsSchema(Schema):
    player_id: int
    season_id: int
    team_id: int
    rank: int
    player: str
    team: str
    gp: int
    min: float
    fgm: float
    fga: float
    fg_pct: float
    fg3m: float
    fg3a: float
    fg3_pct: float
    ftm: float
    fta: float
    ft_pct: float
    oreb: float
    dreb: float
    reb: float
    ast: float
    stl: float
    blk: float
    tov: float
    pf: float
    pts: float
    eff: float
    ast_tov: float
    stl_tov: float
    date: str
