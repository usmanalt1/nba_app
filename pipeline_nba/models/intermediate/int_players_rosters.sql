-- int_player_team_history.sql
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
    r.run_timestamp
FROM {{ ref('stg_nba_players') }} p
left join {{ ref('stg_nba_rosters') }} r
    on CAST(p.player_id AS STRING) = r.player_id
    and p.season_id = r.season_id
    and p.run_timestamp = r.run_timestamp
