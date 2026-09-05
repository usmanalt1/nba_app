VIEWS_PLAYER_STATS_SCHEMA_CONTEXT = """
View: nba_analytics.view_player_stats
Grain: one row per player per game.

Columns:
- player_name (text): Full name of the player.
- team_name (text): Name of the team the player played for in this game.
- game_date (date): Date the game was played.
- wl (text): Outcome for the player's team in this game - 'W' for win, 'L' for loss.
- min (float): Minutes played.
- fgm (float): Field goals made.
- fga (float): Field goals attempted.
- fg_pct (float): Field goal percentage (fgm / fga).
- fg3m (float): Three-point field goals made.
- fg3a (float): Three-point field goals attempted.
- fg3_pct (float): Three-point field goal percentage (fg3m / fg3a).
- ftm (float): Free throws made.
- fta (float): Free throws attempted.
- ft_pct (float): Free throw percentage (ftm / fta).
- oreb (float): Offensive rebounds.
- dreb (float): Defensive rebounds.
- reb (float): Total rebounds (oreb + dreb).
- ast (float): Assists.
- stl (float): Steals.
- blk (float): Blocks.
- tov (float): Turnovers.
- pf (float): Personal fouls.
- pts (float): Points scored.
- plus_minus (float): Point differential while the player was on the court.
- season (text): Season identifier, e.g. '2023-24'.
"""

VIEWS_TEAM_STATS_SCHEMA_CONTEXT = """
View: nba_analytics.view_team_stats
Grain: one row per team per game.

Columns:
- team_name (text): Name of the team.
- game_date (date): Date the game was played.
- wl (text): Outcome for the team in this game - 'W' for win, 'L' for loss.
- min (float): Minutes played (team total).
- fgm (float): Field goals made.
- fga (float): Field goals attempted.
- fg_pct (float): Field goal percentage (fgm / fga).
- fg3m (float): Three-point field goals made.
- fg3a (float): Three-point field goals attempted.
- fg3_pct (float): Three-point field goal percentage (fg3m / fg3a).
- ftm (float): Free throws made.
- fta (float): Free throws attempted.
- ft_pct (float): Free throw percentage (ftm / fta).
- oreb (float): Offensive rebounds.
- dreb (float): Defensive rebounds.
- reb (float): Total rebounds (oreb + dreb).
- ast (float): Assists.
- stl (float): Steals.
- blk (float): Blocks.
- tov (float): Turnovers.
- pf (float): Personal fouls.
- pts (float): Points scored.
- plus_minus (float): Point differential for the team in this game.
- season (text): Season identifier, e.g. '2023-24'.
"""
