select
    p.player_id,
    p.season_id,
    p.player_name,
    r.age,
    r.position,
    p.first_name,
    p.last_name,
    p.is_active,
    p.season,
    -- From the players spine, so it survives a roster row that does not match.
    p.run_timestamp
FROM {{ ref('stg_nba_players') }} p
left join {{ ref('stg_nba_rosters') }} r
    on CAST(p.player_id AS VARCHAR) = r.player_id
    and p.season = r.season
