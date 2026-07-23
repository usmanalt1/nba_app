SELECT
    player_id,
    season,
    description,
    month,
    week,
    run_timestamp
FROM {{ get_latest_by_run_timestamp('player_awards', 'season') }}