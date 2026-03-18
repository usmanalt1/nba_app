-- int_player_team_history.sql
WITH player_team_dates AS (
    SELECT
        player_id,
        player_name,
        team_id,
        team_abbreviation,
        season_id,
        MIN(game_date) AS first_game_with_team,
        MAX(game_date) AS last_game_with_team
    FROM {{ ref('stg_nba_player_logs') }}
    GROUP BY player_id, player_name, team_id, team_abbreviation, season_id
)

SELECT
    player_id,
    player_name,
    team_id,
    team_abbreviation,
    season_id,
    first_game_with_team,
    last_game_with_team,
    COUNT(*) OVER (PARTITION BY player_id, season_id) > 1 AS was_traded
FROM player_team_dates