-- One row per team per game, and exactly one row flagged is_latest per team-season.
select season_id, team_id, game_id, 'duplicate grain' as problem
from {{ ref('mart_team_game_form') }}
group by season_id, team_id, game_id
having count(*) > 1

union all

select season_id, team_id, cast(null as varchar), 'latest game not unique'
from {{ ref('mart_team_game_form') }}
group by season_id, team_id
having sum(case when is_latest then 1 else 0 end) <> 1
