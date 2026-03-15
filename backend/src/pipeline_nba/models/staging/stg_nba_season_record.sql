select
	season,
	CAST(season_id AS STRING) AS season_id,
	run_timestamp
FROM {{ source('nba_dataset', 'season_record') }}