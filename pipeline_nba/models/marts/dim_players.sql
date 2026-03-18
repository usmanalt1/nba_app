-- scd1 dim players - rewritten everytime
SELECT
    *
FROM {{ ref('int_players_rosters') }}
