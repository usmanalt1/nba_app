-- scd1 dim rosters - rewritten everytime
SELECT 
    player_id,
    player_name,
    team_id,
    team_abbreviation,
    season_id,
    season,
    first_game_with_team,
    last_game_with_team,
    was_traded
FROM {{ ref('int_player_team_history') }}