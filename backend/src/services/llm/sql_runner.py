import logging
from typing import Any

import psycopg2
import psycopg2.extras
import sqlglot
from django.db import connection
from sqlglot import exp

from config.settings import settings

logger = logging.getLogger(__name__)

# the only tables the LLM is allowed to query - kept in sync with the views
# described in services/llm/context_schemas.py
ALLOWED_TABLES = {"view_player_stats", "view_team_stats"}

MAX_ROWS = 200
STATEMENT_TIMEOUT_MS = 5000


class SqlValidationError(ValueError):
    pass


def validate_select_only(query: str) -> None:
    try:
        statements = [s for s in sqlglot.parse(query, read="postgres") if s is not None]
    except Exception as e:
        raise SqlValidationError(f"Could not parse query: {e}")

    if len(statements) != 1:
        raise SqlValidationError("Only a single SQL SELECT statement is allowed per query.")

    statement = statements[0]
    if not isinstance(statement, exp.Select):
        raise SqlValidationError("Only SELECT statements are allowed.")

    tables = {t.name for t in statement.find_all(exp.Table)}
    disallowed = tables - ALLOWED_TABLES
    if disallowed:
        raise SqlValidationError(
            f"Query references tables outside the allowed analytics views {sorted(ALLOWED_TABLES)}: "
            f"{sorted(disallowed)}"
        )


class SqlRunner:
    # relies on the llm_readonly Postgres role (see backend/src/app/migrations/0014_llm_roles.py)
    # for the real enforcement - SELECT-only, no access outside the nba_analytics schema. The
    # validation above is a second layer so bad queries fail fast with a message the model can act on.
    def __init__(self):
        # host/port/dbname come from Django's own connection settings rather than config.settings -
        # DB_HOST there defaults to a value nothing ever actually sets, since this stack's real
        # Postgres hostname is configured directly in app/settings.py's DATABASES.
        db = connection.settings_dict
        self.dsn = (
            f"host={db['HOST']} port={db['PORT']} dbname={db['NAME']} "
            f"user={settings.LLM_DB_USER} password={settings.LLM_DB_PASSWORD}"
        )

    def run(self, query: str) -> list[dict[str, Any]]:
        validate_select_only(query)

        with psycopg2.connect(self.dsn) as conn:
            conn.set_session(readonly=True)
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"SET statement_timeout = {STATEMENT_TIMEOUT_MS}")
                cur.execute("SET search_path TO nba_analytics")
                cur.execute(query)
                rows = cur.fetchmany(MAX_ROWS)
                return [dict(row) for row in rows]
