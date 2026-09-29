#!/usr/bin/env bash
# Wrapper around orchestra-cli.
#
# Two annoyances it removes: the CLI needs Python 3.10+ so it lives in its own
# .venv-orchestra rather than the project's 3.9 venv, and every command except
# `pipeline validate` needs ORCHESTRA_API_KEY exported.
#
#   ./orchestra/cli.sh pipeline validate orchestra/nba_dbt_pipeline.yml
#   ./orchestra/cli.sh pipeline new -a nba_dbt -p orchestra/nba_dbt_pipeline.yml
#   ./orchestra/cli.sh pipeline list
#
# The key is read from .env (gitignored) if it isn't already in the environment.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI="$REPO_ROOT/.venv-orchestra/bin/orchestra-cli"

if [[ ! -x "$CLI" ]]; then
  echo "orchestra-cli not installed. Run:" >&2
  echo "  python3.12 -m venv $REPO_ROOT/.venv-orchestra" >&2
  echo "  $REPO_ROOT/.venv-orchestra/bin/pip install orchestra-cli" >&2
  exit 1
fi

if [[ -z "${ORCHESTRA_API_KEY:-}" && -f "$REPO_ROOT/.env" ]]; then
  # Read only this one key rather than sourcing .env, which holds unquoted
  # values that a `source` would choke on or leak into the environment.
  line="$(grep -m1 '^ORCHESTRA_API_KEY=' "$REPO_ROOT/.env" || true)"
  if [[ -n "$line" ]]; then
    value="${line#ORCHESTRA_API_KEY=}"
    value="${value%\"}"; value="${value#\"}"
    value="${value%\'}"; value="${value#\'}"
    export ORCHESTRA_API_KEY="$value"
  fi
fi

cd "$REPO_ROOT"
exec "$CLI" "$@"
