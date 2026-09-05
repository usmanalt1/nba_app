select 
    dt.team_name,
    dg.game_date,
    tps.wl,
    tps.min,
    tps.fgm,
    tps.fga,
    tps.fg_pct,
    tps.fg3m,
    tps.fg3a,
    tps.fg3_pct,
    tps.ftm,
    tps.fta,
    tps.ft_pct,
    tps.oreb,
    tps.dreb,
    tps.reb,
    tps.ast,
    tps.stl,
    tps.blk,
    tps.tov,
    tps.pf,
    tps.pts,
    tps.plus_minus,
    tps.season
from {{ ref('fct_team_stats') }} as tps
-- dim_teams is a current-snapshot dim (one row per team, rewritten every run) not a
-- historical one - joining on season_id here would only ever match whatever single
-- season the last run captured, so it's deliberately left out.
left join {{ ref('dim_teams') }} as dt
    on tps.team_id = dt.team_id
left join {{ ref('dim_games') }} as dg
    on tps.game_id = dg.game_id