---
name: reviewable-code
description: How to write and shape changes in this repo so they can be reviewed quickly. Load before writing or editing code, and before reporting a change set back. Covers scope discipline, function shape, naming, diff hygiene, and what to tell the reviewer. Pairs with the code-comments skill.
---

# Reviewable changes

The reader is reviewing this to decide whether to keep it. Optimise for that, not for
cleverness or for fewest lines.

## Scope

- **One concern per change.** If a fix is needed to make the requested thing work, it is
  in scope - but name it separately when reporting.
- **Never bundle drive-by edits.** No reformatting, no renaming in passing, no "while I
  was here" tidying. They inflate the diff and bury the real change.
- **Touch the fewest files that does the job.** If a change reaches into eight files, say
  why in one line before writing it.
- Leave unrelated code alone even when it is wrong. Mention it instead.

## Shape

- A function should fit on one screen. If it does not, it is doing two things.
- Prefer early returns over nesting. Three levels of indentation is a smell.
- Name things so the call site reads as a sentence: `persist_predictions(...)`,
  `season_type_from_game_id(...)`.
- No single-letter names outside a tight comprehension or loop index.
- Make the common path obvious and the edge case explicit, not the reverse.
- Pull a magic value into a named constant at module level: `SHRINKAGE_GAMES = 10`.

## Diff hygiene

- Keep existing formatting, quote style and import order. Match the file you are in.
- Change the minimum lines needed. Do not rewrite a block to insert one line.
- Keep a rename or a move in its own change, separate from behaviour.
- Do not reorder functions, imports or dict keys unless that is the change.

## Python / Django here

- Services go under `backend/src/services/<area>/`, API routers under `backend/src/api/`.
- Route ordering matters: a `{param}` route swallows literal paths registered after it.
- Prefer a query that returns what is needed over fetching rows and filtering in Python.
- Migrations: one concern each, reversible where it can be, no data repair fused to a
  schema change unless the schema change requires it.

## dbt here

- Logic that two models share goes in a macro, not copied.
- A model selects named columns, never `*` into a mart.
- Classification rules (season type, flags) live in one place.

## React here

- Data fetching in a hook, rendering in the component.
- Pass data down as props rather than refetching in a child.
- A component that needs a value its parent already has takes a prop; it does not call
  the API again.

## Reporting the change

End with, briefly:

1. What was asked for, and where it lives.
2. Anything fixed that was not asked for, and why it was necessary.
3. What was deliberately left out.
4. Which two or three files carry the real judgement and should be read closely - the
   rest is usually mechanical.

State what was verified and how, in plain terms. Never imply a check that was not run.
