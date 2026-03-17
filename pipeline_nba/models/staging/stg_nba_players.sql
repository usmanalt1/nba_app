SELECT
    id AS player_id,
    full_name AS player_name,
    first_name,
    last_name,
    is_active,
    CAST(season_id AS STRING) AS season_id,
    season,
    run_timestamp
FROM {{ source('nba_dataset', 'players_info') }}