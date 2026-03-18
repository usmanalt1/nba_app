-- scd1 dim players - rewritten everytime
SELECT
    s.season_id,
    s.season as season_name,
FROM {{ ref('stg_nba_season_record') }} s
