---
name: worm-colour
description: How to add colour to the Worm NBA app — real team colours (dbt seed through to a React provider and TeamChip), percentile and diverging data scales, gold for milestones, and the team-washed hero. Use whenever implementing or extending the colour pass, touching how teams are shown (chips, prediction bars, game cards, leaderboards, standings), shading tables or stats by rank, building hot/cold or plus/minus visuals, or when the user says the site looks flat, vanilla, or wants more colour. Works alongside worm-design-system, which still owns layout and type; this skill overrides its "one orange thing" rule for team and data colour.
---

# Worm colour pass

The app used to put all its colour into brand orange on grey, which read as vanilla. This pass adds colour that *means something*, in three layers:

1. **Team colour.** Identity: who is this player or team?
2. **Data colour.** Judgement: is this number good or bad, hot or cold?
3. **Gold.** Moments: awards, milestones, season highs.

Brand orange stays the brand: one per section, for "look here". Team and data colour don't count against that limit, but each use must encode something, never decorate.

`assets/colour-study.html` is the approved visual target, with a Current / With colour toggle. Open it before starting and match it.

## Rules

**Team colour**
- Always use `display_hex` from the seed, never raw `primary_hex`. Primaries like Nuggets navy or Bucks green vanish on `--panel`. Every display and alt colour passes 3:1 against `--panel`, as checked by `scripts/check_contrast.py`.
- Allowed places: chips, bar and probability fills, 2–3px left rules on cards, leaderboard tracks (≤ 14% wash, 26% for the leader), the hero wash, and lightly tinted big abbreviations.
- Not allowed: body text, panel backgrounds above ~14% wash, and data scales. Team colour never says good or bad.
- **Matchups:** when two teams sit side by side (prediction bars, game cards, hero), switch the *away* team to `alt_display_hex` if the two display colours are within RGB distance 45. The league is mostly red and blue, so this fires constantly. Route every matchup through `teamPair()` (below) so it's handled in one place.
- **Unknown team** (missing from the seed, or a name mismatch): fall back to `--away`/`--home` in matchups, and to a `--panel-2` chip with `--paper-dim` text elsewhere. Never crash or render a blank chip.
- Chip text is `--ink` when the colour's relative luminance is > 0.5, otherwise white.

**Data colour**
- **Diverging scale** for anything with a meaningful middle: form delta vs season, plus/minus, percentile vs league median. Cold = `--cold` (#3e8ede), hot = `--hot` (#e8622c), and the middle is transparent.
- **Percentile shading:** no fill between the 42.5th and 57.5th percentile. Outside that band, alpha scales from 0.08 to 0.5 at the extremes. Compute percentiles against the *full qualified league* for that season (using the minimum-games rule from `worm-analytics`), never just the rows on screen.
- **Lower-is-better stats** (TOV, DRtg, losses) invert before shading, so orange always means good.
- **Legend:** every shaded table or chart shows the ramp legend (Bottom → Top).
- **Not by hue alone:** the number, the +/− sign, or the bar direction must also carry the meaning.

**Gold (`--gold`)**
- Only for awards (Player of the Week/Month), triple-doubles, season or career highs, and streak milestones (10+).
- Render it as a solid badge with `--ink` text. It never appears in charts.

## Implementation order

Do these in order. Each step is shippable on its own.

### 1. Seed and model (pipeline)

1. Copy `assets/team_colours.csv` to `pipeline_nba/seeds/team_colours.csv`. The `seeds/` dir doesn't exist yet, but `seed-paths` is already set in `dbt_project.yml`.
2. Add `seeds/seeds.yml` with column types (`team_id` int, hex columns varchar) and tests: `unique` + `not_null` on `team_id` and `abbreviation`, and `not_null` on `display_hex` and `alt_display_hex`.
3. Left join the seed into `dim_teams` on `team_id`, adding `display_hex` and `alt_display_hex`.
4. Add both fields (nullable) to the `DimTeams` Django model.
5. Run `python .claude/skills/worm-colour/scripts/check_contrast.py pipeline_nba/seeds/team_colours.csv`. It must exit 0 (no contrast failures, and no clash the alt swap can't fix). Re-run it whenever a colour changes. The Jazz rebranded in 2025, so verify their row first.

### 2. API

- Add `GET /api/nba/db/team_colours` returning `[{team_id, abbreviation, team_name, display_hex, alt_display_hex}]` for the latest season. Cache it in Redis with a long TTL, since it changes about once a year.
- Don't bolt colours onto every endpoint. The frontend joins client-side.

### 3. Frontend foundation

- **`index.css`:** add `--hot: #e8622c; --cold: #3e8ede;`, with a comment that team colours come from the API, not tokens.
- **`src/lib/colour.ts`:**
  - `percentile(value, population, { lowerIsBetter })` → 0..1
  - `shade(p)` → rgba string or `'transparent'`, per the rules above
  - `diverging(delta, maxAbs)` → `{ side: 'up' | 'down', widthPct }`
  - `rgbDistance(a, b)`, `chipText(hex)`
- **`src/context/TeamColoursProvider.tsx`:** fetch once inside the authenticated shell, and build lookups by `team_id`, `abbreviation`, **and** normalised `team_name`. Many endpoints only return `home_team_name`/`away_team_name`, so the name lookup is essential. Expose:
  - `useTeam(key)` → `{ colour, alt, text, abbr, name } | null`
  - `teamPair(awayKey, homeKey)` → `{ away, home }`, with the clash swap and fallbacks applied
- **`src/components/ui/TeamChip.tsx`:** 30×20px, 2px radius, mono 700 10px abbreviation, `title` = full name, with the neutral fallback for unknown teams. Every team mention in the app should eventually render one.

### 4. Apply, highest impact first

1. **`PredictionBar`:** add chips and team-coloured fills via `teamPair`.
2. **`GamesInfo`:** chips replace the coloured dots.
3. **`Leaderboard`:** add an optional `teamKey` on `LeaderboardRow`, which switches the track to the team wash. The leader gets the stronger wash and a 2px team rule. Rows without a `teamKey` keep today's orange behaviour.
4. **Hero:** feature the closest call on tonight's slate. Use a two-team gradient (`color-mix` 42% → 10% from each edge into `--ink`) and faint court lines (SVG at 7% paper opacity). Copy the structure from the colour study.
5. **Hot & cold / form views:** diverging bars from `diverging()`.
6. **Data tables** (`ViewData`, `TeamDataTable`, `AdvancedDataTable`): add percentile cell shading via mantine-datatable's per-column `cellsStyle`, with the legend under the table. Put it behind a toggle, off by default on very wide tables.
7. **Standouts and awards:** gold badges.

## Checks before calling it done

- [ ] `check_contrast.py` exits 0.
- [ ] Every matchup goes through `teamPair` (grep matchup components for `var(--home)` / `var(--away)`).
- [ ] No hex literals in components. Team colours come from the provider, and data colours from `lib/colour.ts` or tokens.
- [ ] Shaded views have a legend, and lower-is-better stats are inverted.
- [ ] An unknown team renders a neutral chip, not an error.
- [ ] Brand orange is still at most one emphasis per section.
- [ ] Side by side with `assets/colour-study.html`, the page isn't louder than the study. If it is, pull the washes back.
