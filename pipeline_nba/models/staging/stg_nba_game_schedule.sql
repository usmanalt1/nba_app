SELECT
    game_id,
    CAST(game_date AS DATE) AS game_date,
    CAST(season_id AS VARCHAR) AS season_id,
    season,
    home_team_id,
    away_team_id,
    game_status,
    run_timestamp
FROM {{ get_latest_by_run_timestamp('game_schedule', 'game_id') }}
