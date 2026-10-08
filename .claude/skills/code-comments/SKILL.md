---
name: code-comments
description: Comment and docstring style for this repo. Load before writing or editing any code file here - Python, TypeScript, SQL or dbt - including new functions, migrations, dbt models and React components. Use when adding comments, writing docstrings, or reviewing a diff for verbosity.
---

# Comments

Default to none. Code that reads clearly needs no narration.

## Write a comment only when

- A non-obvious constraint would be re-broken without it ("must stay registered before X or routing swallows it").
- A line looks wrong but is deliberate ("shift(1) so a game never sees its own result").
- A magic number needs a source ("SHRINKAGE_GAMES = 10, ~half a season's weight").

## Never write

- Narration of what the next line does.
- The history of a bug, how it was found, or what it broke. That belongs in the commit message.
- Restating a parameter list or return type already in the signature.
- Multi-paragraph preambles on a function, migration or dbt model.

## Size

One line. Two if the constraint genuinely needs it. If a comment runs past three lines, the explanation belongs in the commit message or a design note, not the source.

## Docstrings

Only on functions whose purpose is not clear from the name plus signature. One line, imperative. Skip them on migrations, React components, dbt models and obvious helpers.

```python
# good
def previous_season(season_year: str) -> str:
    """e.g. "2026-27" -> "2025-26"."""

# bad - name and signature already say this
def persist_predictions(strategy, season, season_type, predictions) -> dict:
    """Persist the given predictions for the given strategy, season and season type.

    This exists because a live run only predicts games that have not been played,
    and the Redis cache holds only the latest run, so by the time a game has a
    result the prediction made about it is already gone...
    """
```

## SQL and dbt

A model needs no header comment. Comment a `case` arm or join condition only where the encoding is not self-evident (`-- 1xxxx preseason, 2xxxx regular, 4xxxx playoffs`).
