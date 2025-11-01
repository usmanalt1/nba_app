
select 
	p.season_id, 
	p.player_id, 
	p.team_id, 
	p.player, 
	p.team, 
	p.rank as players_season_rank, 
	p.gp as games_played,
	p.fg_pct as field_goal_percentage,
	p.ft_pct as free_throw_percentage,
	p.fg3_pct as three_point_percentage,
	p.oreb/p.gp as offensive_rebounds_per_game,
	p.dreb/p.gp as defensive_rebounds_per_game,
	p.pts/ p.gp as points_per_game,
	p.reb/p.gp as rebounds_per_game,
	p.ast/p.gp as assists_per_game,
	p.stl/p.gp as steal_per_game,
	p.blk/p.gp as blocks_per_game,
	p.tov/p.gp as turnover_per_game
from {{ source("nba_test", "app_playerstats") }} p

