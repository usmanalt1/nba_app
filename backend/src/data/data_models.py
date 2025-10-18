from typing import Optional
from sqlmodel import SQLModel, Field

class SeasonRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    season_id: int

class TeamInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    season_id: int
    abbreviation: str
    nickname: str
    city: str
    state: str
    year_founded: int

class PlayerInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    season_id: int
    full_name: str
    first_name: str
    last_name: str
    is_active: bool

class TeamRoster(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_id: int
    player_id: int
    season_id: int
    player: str
    age: Optional[int]
    position: Optional[str]

class PlayerStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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

class TeamStats(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    group_value: str
    season_id: int
    team_id: int
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
