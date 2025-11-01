select 
*,
rank() over (partition by season_id, season_year order by team_win_percentage desc) as team_season_rank
from {{ ref("stg_nba_team_stats") }}