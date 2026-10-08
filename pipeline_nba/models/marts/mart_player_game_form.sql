{% set by_player = 'partition by season_id, player_id order by game_date, game_id' %}
{% set last_10 = by_player ~ ' rows between 9 preceding and current row' %}
{% set before_last_10 = by_player ~ ' rows between unbounded preceding and 10 preceding' %}

with player_games as (
    -- fct_player_stats carries no game_date, so anything ordered in time has to come
    -- through dim_games. Inner join: a row with no game cannot be placed in a sequence.
    select
        p.season_id,
        p.season,
        p.season_type,
        p.player_id,
        p.player_name,
        p.team_id,
        p.game_id,
        g.game_date,
        p.pts,
        p.reb,
        p.ast,
        p.fga,
        p.fta
    from {{ ref('fct_player_stats') }} p
    join {{ ref('dim_games') }} g on g.game_id = p.game_id
),

form as (
    select
        season_id,
        season,
        season_type,
        player_id,
        player_name,
        team_id,
        game_id,
        game_date,
        pts,
        reb,
        ast,

        -- Partitioned on player alone, never player+team: a mid-season trade would
        -- otherwise split one season into two short, separately-averaged runs.
        row_number() over ({{ by_player }}) as game_number,
        count(*) over (partition by season_id, player_id) as games_in_season,

        avg(pts * 1.0) over ({{ last_10 }}) as form_pts,
        avg(reb * 1.0) over ({{ last_10 }}) as form_reb,
        avg(ast * 1.0) over ({{ last_10 }}) as form_ast,
        -- From window totals, not an average of per-game TS%, which would weight a
        -- 1-for-1 night the same as a 12-for-20 night.
        100.0 * sum(pts) over ({{ last_10 }})
            / nullif(2 * (sum(fga) over ({{ last_10 }}) + 0.44 * sum(fta) over ({{ last_10 }})), 0) as form_ts_pct,

        -- The baseline stops 10 rows short of this game so it never overlaps the form
        -- window - "last 10 against the rest of the season", not against itself.
        avg(pts * 1.0) over ({{ before_last_10 }}) as base_pts,
        100.0 * sum(pts) over ({{ before_last_10 }})
            / nullif(2 * (sum(fga) over ({{ before_last_10 }}) + 0.44 * sum(fta) over ({{ before_last_10 }})), 0) as base_ts_pct
    from player_games
)

select
    season_id,
    season,
    season_type,
    player_id,
    player_name,
    team_id,
    game_id,
    game_date,
    game_number,
    games_in_season,
    game_number = games_in_season as is_latest,
    pts,
    reb,
    ast,
    form_pts,
    form_reb,
    form_ast,
    form_ts_pct,
    base_pts,
    base_ts_pct,
    form_pts - base_pts as delta_pts,
    form_ts_pct - base_ts_pct as delta_ts_pct
from form
