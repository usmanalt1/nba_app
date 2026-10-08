from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_fctadvancedplayerseasonstats_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelPredictionHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('strategy', models.CharField(max_length=50)),
                ('season', models.CharField(max_length=20)),
                ('season_type', models.CharField(max_length=20)),
                ('game_id', models.CharField(max_length=20)),
                ('game_date', models.DateField(blank=True, null=True)),
                ('home_team_id', models.IntegerField(blank=True, null=True)),
                ('home_team_name', models.CharField(blank=True, max_length=50, null=True)),
                ('away_team_name', models.CharField(blank=True, max_length=50, null=True)),
                ('home_win_probability', models.FloatField()),
                ('predicted_home_win', models.BooleanField()),
                ('predicted_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'model_prediction_history',
                'indexes': [models.Index(fields=['strategy', 'season', 'season_type'], name='pred_hist_strategy_season_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='modelpredictionhistory',
            constraint=models.UniqueConstraint(fields=('strategy', 'season', 'season_type', 'game_id'), name='prediction_history_unique_strategy_season_game'),
        ),
    ]
