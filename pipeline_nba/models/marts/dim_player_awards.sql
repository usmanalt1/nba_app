-- scd1 dim players - rewritten everytime
SELECT
    player_id,
    season,
    description,
    month,
    week
FROM {{ ref('stg_nba_player_awards') }}
