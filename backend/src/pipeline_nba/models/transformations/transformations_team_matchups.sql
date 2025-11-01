with team_stats as (select 
    *,
    lag(team_id) over (partition by game_id order by team_id) as vs_team_id
from {{ ref("stg_nba_team_matchups") }}
),

opponent_stats as (select 
    game_id as opponent_game_id,
    team_id as opponent_team_id,
    team_points as opponent_points,
    team_field_goal_percentage as opponent_field_goal_percentage,
    team_three_point_percentage as opponent_three_point_percentage,
    team_free_throw_percentage as opponent_free_throw_percentage,
    team_offensive_rebounds as opponent_offensive_rebounds,
    team_defensive_rebounds as opponent_defensive_rebounds,
    team_assists as opponent_assists,
    team_plus_minus as opponent_plus_minus,
    team_blocks as opponent_blocks,
    team_turnovers as opponent_turnovers,
    team_personal_fouls as opponent_personal_fouls
from {{ ref("stg_nba_team_matchups") }}
)

select     
    ts.*,
    os.opponent_points,
    os.opponent_field_goal_percentage,
    os.opponent_three_point_percentage,
    os.opponent_free_throw_percentage,
    os.opponent_offensive_rebounds,
    os.opponent_defensive_rebounds,
    os.opponent_assists,
    os.opponent_plus_minus,
    os.opponent_blocks,
    os.opponent_turnovers,
    os.opponent_personal_fouls
from team_stats ts
left join opponent_stats os
on ts.game_id = os.opponent_game_id
and ts.vs_team_id = os.opponent_team_id