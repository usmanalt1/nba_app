select 
    dp.player_name,
    dt.team_name,
    dg.game_date,
    fps.wl,
    fps.min,
    fps.fgm,
    fps.fga,
    fps.fg_pct,
    fps.fg3m,
    fps.fg3a,
    fps.fg3_pct,
    fps.ftm,
    fps.fta,
    fps.ft_pct,
    fps.oreb,
    fps.dreb,
    fps.reb,
    fps.ast,
    fps.stl,
    fps.blk,
    fps.tov,
    fps.pf,
    fps.pts,
    fps.plus_minus,
    fps.season
from
{{ ref('fct_player_stats') }} as fps
left join {{ ref('dim_players') }} as dp
    on fps.player_id = dp.player_id and fps.season_id = dp.season_id
left join {{ ref('dim_teams') }} as dt
    on fps.team_id = dt.team_id and fps.season_id = dt.season_id
left join {{ ref('dim_games') }} as dg
    on fps.game_id = dg.game_id