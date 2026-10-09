SELECT
    t.team_id,
    t.season_id,
    t.team_name,
    t.team_abbreviation,
    t.nickname,
    t.city,
    t.state,
    t.year_founded,
    t.season,
    t.run_timestamp,
    c.display_hex,
    c.alt_display_hex
FROM {{ ref('stg_nba_teams') }} t
LEFT JOIN {{ ref('team_colours') }} c ON c.team_id = t.team_id
