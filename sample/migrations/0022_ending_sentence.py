# Generated by Django 3.2.9 on 2021-11-09 09:02

import django.db.models.deletion
from django.db import migrations, models

import model_clone.mixin


class Migration(migrations.Migration):
    dependencies = [
        ("sample", "0021_book_custom_slug"),
    ]

    operations = [
        migrations.CreateModel(
            name="Sentence",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("value", models.TextField()),
            ],
            bases=(model_clone.mixin.CloneMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Ending",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sentence",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ending",
                        to="sample.sentence",
                    ),
                ),
            ],
            bases=(model_clone.mixin.CloneMixin, models.Model),
        ),
    ]