from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_playerawards_field_lengths'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerawards',
            name='first_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='last_name',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='team',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='all_nba_team_number',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='season',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='month',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='week',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='conference',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='subtype1',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='subtype2',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='subtype3',
            field=models.TextField(blank=True, null=True),
        ),
    ]
