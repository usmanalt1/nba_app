{{ config(tags=['advanced']) }}

-- Renamed to the same vocabulary as fct_player_stats, and the 0-1 shares scaled to
-- 0-100 so both stat sets read the same way in the UI. ast_to and ast_ratio are
-- already per-100 values from the endpoint, so they pass through untouched.
select
    season,
    season_type,
    player_id,
    player_name,
    team_id,
    team_abbreviation,
    age,
    gp                          as games_played,
    w                           as wins,
    l                           as losses,
    min                         as average_minutes,
    off_rating                  as offensive_rating,
    def_rating                  as defensive_rating,
    net_rating,
    ast_to                      as assist_to_turnover,
    ast_ratio                   as assist_ratio,
    pace,
    poss                        as possessions,
    round((ast_pct    * 100)::numeric, 1)::float as assist_percentage,
    round((oreb_pct   * 100)::numeric, 1)::float as offensive_rebound_percentage,
    round((dreb_pct   * 100)::numeric, 1)::float as defensive_rebound_percentage,
    round((reb_pct    * 100)::numeric, 1)::float as rebound_percentage,
    round((tm_tov_pct * 100)::numeric, 1)::float as turnover_percentage,
    round((efg_pct    * 100)::numeric, 1)::float as effective_field_goal_percentage,
    round((ts_pct     * 100)::numeric, 1)::float as true_shooting_percentage,
    round((usg_pct    * 100)::numeric, 1)::float as usage_percentage,
    round((pie        * 100)::numeric, 1)::float as pie,
    run_timestamp
FROM {{ ref('stg_nba_advanced_player_season_stats') }}
