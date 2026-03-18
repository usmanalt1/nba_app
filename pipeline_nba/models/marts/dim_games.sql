-- scd1 dim players - rewritten everytime
SELECT
*
FROM {{ ref('int_home_away_games') }}
