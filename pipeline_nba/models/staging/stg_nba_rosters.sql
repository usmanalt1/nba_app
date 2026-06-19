SELECT
    CAST(team_id AS VARCHAR)   AS team_id,
    CAST(player_id AS VARCHAR) AS player_id,
    player                    AS player_name,
    age                       AS age,
    position,
    CAST(season_id AS VARCHAR) AS season_id,
    season,
    run_timestamp
FROM {{ get_latest_by_run_timestamp('teams_roster', 'season_id, team_id, player_id') }}