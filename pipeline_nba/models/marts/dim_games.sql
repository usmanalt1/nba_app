SELECT
    game_id,
    game_date,
    season_id,
    season,
    -- game_id, not season_id: this model includes scheduled games
    {{ season_type_from_game_id('game_id') }} as season_type,
    home_team_id,
    home_team_abbreviation,
    home_team_name,
    home_pts,
    home_wl,
    away_team_id,
    away_team_abbreviation,
    away_team_name,
    away_pts,
    away_wl,
    run_timestamp
FROM {{ ref('int_home_away_games') }}
