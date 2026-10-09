from django.db import migrations


def seed_ml_models(apps, schema_editor):
    MlModels = apps.get_model("app", "MlModels")
    # Hardcoded snapshot of STRATEGY_REGISTRY: a migration shouldn't import app code.
    for name in ["logistic_regression", "random_forest"]:
        MlModels.objects.get_or_create(model_name=name)


def unseed_ml_models(apps, schema_editor):
    MlModels = apps.get_model("app", "MlModels")
    MlModels.objects.filter(
        model_name__in=["logistic_regression", "random_forest"]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0012_mlmodels"),
    ]

    operations = [
        migrations.RunPython(seed_ml_models, reverse_code=unseed_ml_models),
    ]
