# Read-only role for the LLM to query through. Grants nothing here on purpose: access to
# nba_analytics is owned by dbt's `+grants`, since those views are rebuilt every run.

from django.db import migrations

from config.settings import settings

ROLE_NAME = settings.LLM_DB_USER


def create_llm_readonly_role(apps, schema_editor):
    connection = schema_editor.connection
    db_name = connection.settings_dict["NAME"]

    with connection.cursor() as cursor:
        # CREATE ROLE has no IF NOT EXISTS, so guard it to stay re-runnable.
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
