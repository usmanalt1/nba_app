from django.db import migrations


def seed_ml_models(apps, schema_editor):
    MlModels = apps.get_model("app", "MlModels")
    # snapshot of STRATEGY_REGISTRY's keys at the time this migration was written -
    # deliberately hardcoded, not imported, since migrations shouldn't depend on
    # app code that can change or move later
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
