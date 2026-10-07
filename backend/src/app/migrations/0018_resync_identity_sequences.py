from django.db import migrations

# players_info.id and teams_info.id hold NBA entity ids written by an older loader, but
# the identity sequences were never advanced past them - so new inserts collide with
# taken ids. Forward-only, safe to re-run.

AFFECTED_TABLES = ["players_info", "teams_info"]


def resync_sequences(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        for table in AFFECTED_TABLES:
            cursor.execute("SELECT pg_get_serial_sequence(%s, 'id')", [table])
            row = cursor.fetchone()
            sequence = row[0] if row else None
            if not sequence:
                continue

            cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table}")
            max_id = cursor.fetchone()[0]

            cursor.execute("SELECT last_value, is_called FROM " + sequence)
            last_value, is_called = cursor.fetchone()
            current = last_value if is_called else last_value - 1

            if max_id > current:
                cursor.execute("SELECT setval(%s, %s, true)", [sequence, max_id])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0017_model_prediction_history"),
    ]

    operations = [
        migrations.RunPython(resync_sequences, noop),
    ]
