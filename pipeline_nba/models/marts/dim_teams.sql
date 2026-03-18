-- scd1 dim players - rewritten everytime
SELECT
    t.team_id,
    t.season_id,
    t.team_name,
    t.team_abbreviation,
    t.nickname,
    t.city,
    t.state,
    t.year_founded,
    t.season
FROM {{ ref('stg_nba_teams') }} t
