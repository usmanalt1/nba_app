WITH home AS (
    SELECT
        game_id,
        game_date,
        season_id,
        season,
        team_id           AS home_team_id,
        team_abbreviation AS home_team_abbreviation,
        team_name         AS home_team_name,
        wl                AS home_wl,
        pts               AS home_pts
    FROM {{ ref('stg_nba_team_logs') }}
    WHERE matchup LIKE '%vs.%'
),
away AS (
    SELECT
        game_id,
        team_id           AS away_team_id,
        team_abbreviation AS away_team_abbreviation,
        team_name         AS away_team_name,
        wl                AS away_wl,
        pts               AS away_pts
    FROM {{ ref('stg_nba_team_logs') }}
    WHERE matchup LIKE '%@%'
)

SELECT
    h.game_id,
    h.game_date,
    h.season_id,
    h.season,
    h.home_team_id,
    h.home_team_abbreviation,
    h.home_team_name,
    h.home_pts,
    h.home_wl,
    a.away_team_id,
    a.away_team_abbreviation,
    a.away_team_name,
    a.away_pts,
    a.away_wl
FROM home h
INNER JOIN away a ON h.game_id = a.game_id