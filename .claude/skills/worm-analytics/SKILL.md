---
name: worm-analytics
description: Roadmap and build rules for analytics in the Worm NBA app (home page sections, the analytics page, dbt marts, analytics API endpoints). Use whenever working on anything in frontend/src/components/Home, a new analytics/insights page, backend/src/services/analytics, backend/src/api/analytics_api.py, or pipeline_nba models that feed stats to the UI — including "add a stat", "what should go on the home page", leaderboards, form/streaks, splits, or charts of player/team data.
---

# Worm analytics

Worm has two analytics surfaces with different jobs. Keep them separate. Most bad decisions here come from putting reference stats on the home page.

- **Home (`/`)** answers *"what's happening right now and what's next?"* It's recent, short, and opinionated, and it changes daily.
- **Analytics page (new route, e.g. `/analytics`)** answers *"who is actually good, and why?"* It's deep, filterable by season/season type, and stable.
- Model-evaluation views (Model Bench, calibration) belong on the Predictions/Wormhole page, not on home.

When adding something, ask: would this be different tomorrow? If yes, it goes on home. If no, it goes on the analytics page.

## Target home page

Order matters. Lead with the future, then the recent past, then the model.

1. **Hero + Model Pulse.** Keep these as they are.
2. **Tonight's slate.** Upcoming games from `stg_nba_game_schedule` (filter by `game_status`, next game date), each with Worm's pick and confidence using `PredictionBar`. This is the most important missing section.
3. **Around the League.** Recent finals (existing `Games`).
4. **Standout performances.** From the last game date: 30+ pts, triple-doubles (3 of pts/reb/ast/stl/blk ≥ 10), top plus/minus. Max ~8 cards.
5. **Hot & cold.** Players and teams whose last 10 games deviate most from their season average. For players use PPG and TS%. For teams use avg margin and record. Show both directions.
6. **Standings snapshot.** Top 6 per conference with W-L, win %, and current streak.
7. **Latest Calls / Burned.** Keep these.
8. **Award strip.** Latest Player of the Week/Month from `dim_player_awards`, which is collected but currently unused.

Move off home: Player Leaders, Team Leaders, Most Improved, and Model Bench.

## Target analytics page

Every section takes season + season type from shared filter state. Reuse `ViewDataFiltersContext` or a sibling context, rather than per-component state.

- **Team quadrant.** ORtg (x) vs DRtg (y, inverted so up = good) from `fct_advanced_team_season_stats`. Draw league-average crosshairs and label the quadrants. Add pace vs net rating as a second view.
- **Player efficiency.** Usage % vs TS % scatter (minimum games filter) from `fct_advanced_player_season_stats`. Put PIE and net rating leaderboards beside it.
- **Leaderboards.** Moved here from home. Add stl, blk, tov, and shooting %, which already exist in `fct_player_stats` but aren't surfaced.
- **Rolling form.** Rolling 10-game line for a selected player or team over the season.
- **Splits.** Home/away, wins/losses, and rest (back-to-back vs 1 day vs 2+ days, derived from consecutive game dates). These double as candidate model features, so note that when building them.
- **Consistency.** Points std dev and % of games above own average ("reliable vs boom-or-bust").
- **Most improved.** Players and teams, moved from home.
- **League trends.** By season: pace, PPG, 3PA share of FGA. Uses every loaded season.

## Where the logic lives

Prefer dbt over per-request pandas. The current analytics endpoints pull whole fact tables into pandas on every request. New work should do this instead:

1. Build the aggregation as a dbt mart in `pipeline_nba/models/marts/`, documented and tested in `marts_models.yml` (`not_null`/`unique` on the grain). Suggested marts:
   - `mart_player_game_form`: per player-game, rolling 5/10 pts/reb/ast/TS%, season-to-date averages, and a rest-days column.
   - `mart_team_game_form`: the same for teams, plus margin, streak length and streak type.
   - `mart_player_splits` and `mart_team_splits`: home/away, W/L, and rest buckets.
   - `mart_standings`: W, L, win %, streak, and conference rank per season.
2. Add an unmanaged Django model pointing at `"nba_marts"."<mart>"`, following the existing `Dim*`/`Fct*` models in `app/models.py`.
3. Add a thin endpoint in `analytics_api.py` that filters and returns. Keep the existing `NBADataResponseSchema` envelope (`success`/`error`/`records`) and `AsyncJWTAuth`.
4. Cache responses in Redis. Key on endpoint + season + season_type, and invalidate on dbt run. Key constants live in `services/redis/redis_key_constants.py`.

Pandas in `services/analytics/` is fine for small reshaping. Don't use it for anything a SQL window function does better.

## Data gotchas (verified in the repo)

- **`fct_player_stats` and `fct_team_stats` have no `game_date` or `matchup`.** Join `dim_games` on `game_id` for dates and home/away. Anything time-ordered (form, streaks, rest, "last night") needs this join.
- **Traded players split across rows.** `PlayerStats` and `MostImprovedPlayers` group by `team_id`, so a mid-season trade produces two partial rows that can each miss the games threshold. Group by `player_id, season_id` and attach the most recent team separately. Fix this when touching either class.
- **Season type is detected inconsistently.** dbt uses `season_id like '%420%'`, while `HomeTeamLeaders` uses `season_id.startsWith("42")`. Use the `season_type` column everywhere and don't re-derive it.
- **Early-season samples are tiny.** In October/November the current season has a handful of games. `MostImprovedPlayers` (MIN_GAMES = 20) returns nothing, and per-game leaderboards are noise. Every section needs a minimum-games rule and an explicit fallback: show last season with a "2025-26 final" label, or an "early season" empty state. Never show an empty panel with no explanation.
- **Advanced stats are season-level only.** There are no per-game advanced stats. Compute game-level TS% yourself as `pts / (2 * (fga + 0.44 * fta))`.
- **Playoff advanced stats** may have very low game counts. Apply the same minimum-games rule.

## Metric definitions

Use these consistently so numbers match across pages.

- **TS%**: `pts / (2 * (fga + 0.44 * fta))`.
- **Hot/cold delta**: last-10 average minus season-to-date average *excluding* those 10 games. Require ≥ 20 season games.
- **Streak**: consecutive identical `wl` ending at the most recent game.
- **Rest days**: days since the team's previous game minus 1. 0 = back-to-back.
- **Triple-double**: ≥ 10 in at least three of pts, reb, ast, stl, blk.

## Definition of done for an analytics feature

- [ ] Logic in a dbt mart with tests, or a justified pandas transform.
- [ ] Endpoint returns the standard envelope, is JWT-protected, and is Redis-cached.
- [ ] TypeScript interface added in `frontend/src/types/`.
- [ ] Minimum-games rule and early-season fallback handled.
- [ ] UI built with the `worm-design-system` skill.
- [ ] Section placed on the correct page per the rule at the top.
