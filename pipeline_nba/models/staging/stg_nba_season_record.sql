select
	season,
	CAST(season_id AS STRING) AS season_id,
	run_timestamp
FROM {{ get_latest_by_run_timestamp('season_record', 'season_id') }}