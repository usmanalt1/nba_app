{{ config(tags=['advanced']) }}

SELECT *
FROM {{ get_latest_by_run_timestamp('advanced_player_season_stats', 'season, season_type, player_id') }}
