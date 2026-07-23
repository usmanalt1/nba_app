from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_playerawards'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playerawards',
            name='team',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='month',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='playerawards',
            name='week',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
