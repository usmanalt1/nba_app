SELECT
    id                        AS team_id,
    full_name                 AS team_name,
    abbreviation              AS team_abbreviation,
    nickname,
    city,
    state,
    year_founded,
    CAST(season_id AS STRING) AS season_id,
    season,
    run_timestamp
FROM {{ get_latest_by_run_timestamp('teams_info', 'id, season_id') }}