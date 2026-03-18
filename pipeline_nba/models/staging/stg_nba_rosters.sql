SELECT
    CAST(team_id AS STRING)   AS team_id,
    CAST(player_id AS STRING) AS player_id,
    player                    AS player_name,
    CAST(age AS FLOAT64)      AS age,
    position,
    CAST(season_id AS STRING) AS season_id,
    season,
    run_timestamp
FROM {{ get_latest_by_run_timestamp('teams_roster', 'season_id, team_id, player_id') }}