{{ config(tags=['advanced']) }}

SELECT *
FROM {{ get_latest_by_run_timestamp('advanced_team_season_stats', 'season, season_type, team_id') }}
