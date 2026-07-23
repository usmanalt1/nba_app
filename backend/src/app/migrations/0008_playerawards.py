from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_add_fk_fct_player_stats_player'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerAwards',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_id', models.IntegerField()),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=50, null=True)),
                ('team', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.CharField(max_length=100)),
                ('all_nba_team_number', models.CharField(blank=True, max_length=5, null=True)),
                ('season', models.CharField(blank=True, max_length=20, null=True)),
                ('month', models.CharField(blank=True, max_length=20, null=True)),
                ('week', models.CharField(blank=True, max_length=20, null=True)),
                ('conference', models.CharField(blank=True, max_length=20, null=True)),
                ('subtype1', models.CharField(blank=True, max_length=50, null=True)),
                ('subtype2', models.CharField(blank=True, max_length=50, null=True)),
                ('subtype3', models.CharField(blank=True, max_length=50, null=True)),
                ('run_timestamp', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'player_awards',
            },
        ),
    ]
