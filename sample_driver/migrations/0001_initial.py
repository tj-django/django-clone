# Generated by Django 3.0.6 on 2020-05-16 17:33

from django.db import migrations, models
import model_clone.mixins.clone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Driver",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("age", models.SmallIntegerField()),
            ],
            bases=(models.Model, model_clone.mixins.clone.CloneMixin),
        ),
    ]
