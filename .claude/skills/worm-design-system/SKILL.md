---
name: worm-design-system
description: The Worm NBA app's visual design system — tokens, typography, primitives (Panel, SectionHeader, StatCard, Leaderboard, PredictionBar, FormStrip, CalibrationChart) and page anatomy — plus the list of pages that don't match it yet. Use for ANY frontend work in frontend/src: building a new page or section, adding a chart, styling a component, restyling an old page, or when the user says something "looks off", "doesn't match", or wants the site to look consistent. Read before writing any JSX or CSS in this repo.
---

# Worm design system

The home page is the reference implementation. Its look is a dark broadcast scoreboard: deep ink background, flat panels with 1px lines, one loud orange accent, mono uppercase labels, and condensed Oswald numbers. Everything new should look like it was built alongside `components/Home/*`. Anything older should be pulled toward it.

Before building, open `src/index.css`, `src/theme.ts`, and `src/components/ui/`. Reuse a primitive before writing new markup.

## Tokens

Never hard-code a hex. Use the CSS variables from `index.css`:

| Role | Variable |
|---|---|
| Page background | `--ink` |
| Raised surface / panel | `--panel` (nested or track: `--panel-2`) |
| Borders, dividers, gridlines | `--line` |
| Primary text / values | `--paper` |
| Secondary text | `--paper-dim` |
| Tertiary, empty states, axis ticks | `--paper-faint` |
| Brand accent | `--worm` (`--worm-deep` for gradients only) |
| Home / away team | `--home` / `--away` |
| Win / loss, hit / miss | `--win` / `--lose` |
| Awards, triple-doubles, season highs | `--gold` |
| Data scale ends (good/hot, bad/cold) | `--hot` / `--cold` |
| Team identity | `--tc` / `--tt`, set per element from the team colour seed (see `worm-colour`) |

Brand tints use `rgba(232, 98, 44, α)`. Use 0.14 for a leader row and 0.04–0.06 for background washes. That's the only rgba in the system besides the shadow.

**Accent discipline:** a section gets one *brand* orange thing. That can be the leader row, the hero number, or the accent rule on the lead panel. If everything is orange, nothing is. Team colour (identity), data colour (meaning) and gold (achievement) are separate layers with their own rules. Follow the `worm-colour` skill whenever a component shows a team, a player or a ranked number.

## Typography

- **Headings and big numbers:** Oswald 600, uppercase for h1/h2. `StatCard` values use 28px, or 42px for a hero.
- **Labels, table heads, axis ticks, eyebrows:** the `.kicker` class (Plex Mono 10px, uppercase, 0.08em tracking). Don't re-create it inline with Mantine `Text` props.
- **Numbers in rows, scores, percentages:** `var(--mono)` with `fontVariantNumeric: 'tabular-nums'`, so columns don't jitter.
- **Body:** Inter, inherited. Don't set it.

## Layout rules

- **Root font-size is 18px.** Mantine's rem-based shorthands (`w`, `h`, `p`, `m`, `size="xl"`, `Box` props) silently scale by 1.125×. Use plain `div`s with pixel `style` for layout, like `Panel` does. Mantine is fine for inputs (`Select`, `TextInput`, `Textarea`, `SegmentedControl`, `Tabs`, `Button`) and their theming.
- **Page wrapper:** `width: 100%`, `maxWidth: 1400`, `margin: '0 auto'`, `paddingBottom: 60`.
- **Sections:** each is a `<section>` with `marginBottom: 'var(--section-gap)'`, opened by `SectionHeader` with a two-digit `index` ("01", "02"…), a `title`, and a one-line `subtitle` that says *what the reader learns*, not what the data is. Filters and legends go in `meta`.
- **Grids:** `display: grid; gridTemplateColumns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20`, as in `HomeTeamLeaders`. Rows of cards that overflow go in a `.rail` (horizontal scroll, scrollbar hidden until hover).
- **Radii:** 4px on panels and cards, 2–3px on bars. Nothing rounder.
- **Spacing:** panel padding is `16px 18px`, and `14px` sits under a panel title. Stick to the existing numbers rather than inventing new ones.
- Borders are 1px `--line`. The only exception is a 2px `--worm` left rule on a section's lead `Panel` (`accent` prop).

## Primitives to reuse

- `Panel`: any boxed content. Has a kicker title, `titleMeta` on the right, and an optional `accent`.
- `SectionHeader`: every top-level section on every page.
- `StatCard`: single KPI with label, value, and note. Supports `tone` (default/brand/win/lose) and `hero`.
- `Leaderboard`: any ranked list. Takes a `magnitude` for the zero-based track behind rows.
- `PredictionBar`: any matchup with probabilities. Away is always on top, home underneath.
- `FormStrip`: any W/L or hit/miss sequence, oldest → newest.
- `CalibrationChart`: the reference for how a custom chart should look and behave.
- `WormMark` / `WormPortrait`: brand. Use sparingly, mostly in heroes and empty states.

If a new visual is needed (scatter, line, quadrant), add it to `components/ui/` as a reusable primitive. Don't bury it in a page.

## Charts

There is no chart library in use. Charts are hand-built from divs/SVG so they inherit the tokens. Keep it that way unless a chart truly needs a library. If one is added, theme it fully to the tokens: no default palettes, no default tooltips, no white backgrounds.

Follow `CalibrationChart`'s conventions:
- The legend sits above the plot using kicker labels.
- Gridlines are 1px `--line`, and tracks are `--panel-2`.
- Axis ticks are kickers in `--paper-faint`.
- Data uses `--worm` for the primary series. Use team colours when series are teams, `--hot`/`--cold` for diverging values, and `--home`/`--away` or `--win`/`--lose` only when that is literally the meaning.
- On hover, dim the other series to ~0.55 opacity with a 120ms transition, and put the readout in a mono caption line *below* the chart instead of a floating tooltip.
- When nothing is hovered, the caption explains how to read the chart in one plain sentence.
- Bars are zero-based, so gaps aren't exaggerated.
- Don't rely on red/green alone. Pair colour with shape or length, as `FormStrip` does with full-height hits vs stub misses.

## Copy and states

- Subtitles and empty states are short, dry, and slightly wry ("No misses on record — yet."). They're never corporate.
- Every data component handles loading, empty, and error states. Empty text is 13px `--paper-faint` inside the panel, not a blank box.
- Dates use `toLocaleDateString(undefined, { month: 'short', day: 'numeric' })`. Separators are ` · `.

## Pages that don't match yet

These are known drift. Fix them when touching the file, or on request:

1. **`CollectData/CollectData.tsx`** has Bootstrap hexes (`#007bff`, `#dc3545`, `#28a745`), a `#f8f9fa` light box, and raw `<button>`s. Rebuild it with `SectionHeader`, Mantine `Button` variants, and `Panel`s. It isn't routed in `App.tsx`, so check with the user whether it should exist at all.
2. **`Predictions/StatTile.tsx`** duplicates `StatCard` using Mantine `Text` props. Replace its usages with `StatCard` and delete it.
3. **`Predictions/Predictions.tsx`** has a filter row with ad-hoc padding, `SimpleGrid` (rem-scaled), and pill `Tabs` with bold 16px labels that fight the mono tab style in `theme.ts`. Move the filters into `SectionHeader` `meta` or a `Panel`, use a pixel CSS grid for the tiles, and use default-styled tabs.
4. **`NbaAi/NbaAi.tsx`** has a raw `<h1>`, an unstyled `<p>`, `Text color="red"`, and "Q:/A:" in `<strong>`. Give it a `SectionHeader`, and render the conversation as panels with kicker labels ("You" / "Worm"). Use `--lose` for errors and a mono caption for timestamps.
5. **`ViewData/ViewDataPage.tsx`** has filters with their own `selectStyle`. Align them with the shared filter treatment and add a `SectionHeader`.
6. **`ScrollableTrends/Trends.tsx`** is a legacy top-3 strip using Mantine `Box`/`Group`/`ScrollArea` and a nested ternary. It's superseded by `Leaderboard`. Remove it if unused, otherwise rebuild it on `Leaderboard` inside a `.rail`.
7. **`Auth/AuthPage`** uses a CSS module. Check that it only references the tokens.
8. **Navbar:** two items share `IconAdjustments` (Predictions and NBAI). Give each page a distinct icon.

## Review checklist

Run this before calling frontend work done:

- [ ] No hex or rgb literals outside `index.css` / `theme.ts` (`grep -rnE "#[0-9a-fA-F]{3,6}" src/components`).
- [ ] No Mantine rem shorthands for layout.
- [ ] Every top-level section has a `SectionHeader` with an index.
- [ ] Labels use `.kicker`, and numbers are mono + tabular.
- [ ] At most one brand-orange emphasis per section, and every other colour has a named job (team, data, gold).
- [ ] Loading, empty, and error states exist.
- [ ] Works at 1024px and below (font-size and `--section-gap` shrink there, so check nothing overflows).
- [ ] New visuals live in `components/ui/` and are reused, not inlined.
