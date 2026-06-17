-- scd1 dim players - rewritten everytime
SELECT
    player_id,
    season_id,
    player_name,
    age,
    position,
    first_name,
    last_name,
    is_active,
    season,
    run_timestamp
FROM {{ ref('int_players_rosters') }}
