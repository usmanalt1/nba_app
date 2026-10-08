{% set by_team = 'partition by season_id, team_id order by game_date, game_id' %}
{% set last_10 = by_team ~ ' rows between 9 preceding and current row' %}
{% set before_last_10 = by_team ~ ' rows between unbounded preceding and 10 preceding' %}

with team_games as (
    -- Same dim_games join as the player form mart: fct_team_stats has no game_date.
    select
        t.season_id,
        t.season,
        t.season_type,
        t.team_id,
        t.game_id,
        g.game_date,
        -- On a team log plus_minus is the final margin; verified equal to
        -- dim_games' home_pts - away_pts for every 2025-26 regular season game.
        t.plus_minus as margin,
        case when t.wl = 'W' then 1 else 0 end as win
    from {{ ref('fct_team_stats') }} t
    join {{ ref('dim_games') }} g on g.game_id = t.game_id
),

form as (
    select
        season_id,
        season,
        season_type,
        team_id,
        game_id,
        game_date,
        margin,
        win,

        row_number() over ({{ by_team }}) as game_number,
        count(*) over (partition by season_id, team_id) as games_in_season,

        avg(margin * 1.0) over ({{ last_10 }}) as form_margin,
        100.0 * avg(win * 1.0) over ({{ last_10 }}) as form_win_pct,
        sum(win) over ({{ last_10 }}) as form_wins,
        count(*) over ({{ last_10 }}) as form_games,

        -- Stops 10 rows short of this game, so form and baseline never overlap.
        avg(margin * 1.0) over ({{ before_last_10 }}) as base_margin,
        100.0 * avg(win * 1.0) over ({{ before_last_10 }}) as base_win_pct
    from team_games
)

select
    season_id,
    season,
    season_type,
    team_id,
    game_id,
    game_date,
    game_number,
    games_in_season,
    game_number = games_in_season as is_latest,
    margin,
    win,
    form_margin,
    form_win_pct,
    form_wins,
    form_games,
    base_margin,
    base_win_pct,
    form_margin - base_margin as delta_margin,
    form_win_pct - base_win_pct as delta_win_pct
from form
