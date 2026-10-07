from django.db import migrations, models

# Move the NBA entity id out of `id`, which is Django's surrogate pk and cannot repeat
# across the per-(entity, season) rows these tables hold. Rows written after the loader
# started discarding the source id cannot be repaired here - re-load those from object
# storage.
NBA_TEAM_ID_MIN = 1610612700
NBA_TEAM_ID_MAX = 1610612800


def backfill_entity_ids(apps, schema_editor):
    TeamInfo = apps.get_model("app", "TeamInfo")
    PlayerInfo = apps.get_model("app", "PlayerInfo")

    TeamInfo.objects.filter(team_id__isnull=True).update(team_id=models.F("id"))
    PlayerInfo.objects.filter(player_id__isnull=True).update(player_id=models.F("id"))

    suspect = TeamInfo.objects.exclude(
        team_id__range=(NBA_TEAM_ID_MIN, NBA_TEAM_ID_MAX)
    ).count()
    if suspect:
        print(
            f"\n  WARNING: {suspect} teams_info row(s) have a team_id outside the NBA's "
            f"id range - they were loaded while the source `id` was being stripped and "
            f"carry a sequence value instead. Re-load those seasons from object storage "
            f"(/load_to_postgres?run_id=...) to replace them with real ids."
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0018_resync_identity_sequences"),
    ]

    operations = [
        migrations.AddField(
            model_name="playerinfo",
            name="player_id",
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="teaminfo",
            name="team_id",
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.RunPython(backfill_entity_ids, noop),
    ]
