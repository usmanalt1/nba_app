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
        pts               AS home_pts,
        run_timestamp
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
        pts               AS away_pts,
        run_timestamp
    FROM {{ ref('stg_nba_team_logs') }}
    WHERE matchup LIKE '%@%'
),
played AS (
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
        a.away_wl,
        a.run_timestamp
    FROM home h
    INNER JOIN away a ON h.game_id = a.game_id and h.run_timestamp = a.run_timestamp
),
-- games on the schedule that don't have a box score yet - future/unplayed games.
-- Once a game is actually played it shows up in `played` above via team_logs, and this
-- CTE excludes it so the real result always wins over the pre-game schedule row.
latest_season_id AS (
    SELECT MAX(season_id) AS season_id
    FROM {{ ref('stg_nba_game_schedule') }}
),

nba_teams as (
    SELECT team_id, team_abbreviation, team_name
    FROM {{ ref('stg_nba_teams') }} team_stats
    inner join latest_season_id lsi on lsi.season_id = team_stats.season_id
),

scheduled AS (
    SELECT
        s.game_id,
        s.game_date,
        s.season_id,
        s.season,
        s.home_team_id,
        ht.team_abbreviation AS home_team_abbreviation,
        ht.team_name         AS home_team_name,
        CAST(NULL AS DOUBLE PRECISION) AS home_pts,
        CAST(NULL AS VARCHAR)          AS home_wl,
        s.away_team_id,
        awt.team_abbreviation AS away_team_abbreviation,
        awt.team_name         AS away_team_name,
        CAST(NULL AS DOUBLE PRECISION) AS away_pts,
        CAST(NULL AS VARCHAR)          AS away_wl,
        s.run_timestamp
    FROM {{ ref('stg_nba_game_schedule') }} s
    LEFT JOIN nba_teams ht ON ht.team_id = s.home_team_id
    LEFT JOIN nba_teams awt ON awt.team_id = s.away_team_id
    WHERE s.game_id NOT IN (SELECT game_id FROM played)
)

SELECT * FROM played
UNION ALL
SELECT * FROM scheduled