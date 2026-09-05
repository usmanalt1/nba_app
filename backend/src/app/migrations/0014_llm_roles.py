# Creates a read-only Postgres role for the LLM analytics feature (and, eventually,
# an MCP server) to query through - kept separate from the "admin" role Django/dbt
# use so that surface can only ever SELECT, never write.
#
# This only creates the role and lets it connect to the database. It intentionally
# grants nothing on `public` or `nba_marts` - the role is meant to see only the
# curated `nba_analytics` schema (dbt's semantic_views models), and those grants are
# owned by dbt's `+grants` config in dbt_project.yml since that schema's views are
# rebuilt on every dbt run.

from django.db import migrations

from config.settings import settings

ROLE_NAME = settings.LLM_DB_USER


def create_llm_readonly_role(apps, schema_editor):
    connection = schema_editor.connection
    db_name = connection.settings_dict["NAME"]

    with connection.cursor() as cursor:
        # CREATE ROLE has no IF NOT EXISTS, so guard it manually to keep the
        # migration safe to re-run (e.g. after `migrate app zero` in dev).
        cursor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = %(role)s) THEN
                    EXECUTE format('CREATE ROLE %%I LOGIN PASSWORD %%L', %(role)s, %(password)s);
                END IF;
            END
            $$;
            """,
            {"role": ROLE_NAME, "password": settings.LLM_DB_PASSWORD},
        )
        cursor.execute(f'GRANT CONNECT ON DATABASE "{db_name}" TO "{ROLE_NAME}"')


def drop_llm_readonly_role(apps, schema_editor):
    connection = schema_editor.connection
    db_name = connection.settings_dict["NAME"]

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_catalog.pg_roles WHERE rolname = %s", [ROLE_NAME])
        if cursor.fetchone() is None:
            return

        cursor.execute(f'REVOKE CONNECT ON DATABASE "{db_name}" FROM "{ROLE_NAME}"')
        cursor.execute(f'DROP ROLE "{ROLE_NAME}"')


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0013_seed_ml_models"),
    ]

    operations = [
        migrations.RunPython(create_llm_readonly_role, reverse_code=drop_llm_readonly_role),
    ]
