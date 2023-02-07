# Generated by Django 3.1.7 on 2021-04-10 13:50

import django.db.models.deletion
from django.db import migrations, models

import model_clone.mixin


class Migration(migrations.Migration):
    dependencies = [
        ("sample", "0009_auto_20210407_1546"),
    ]

    operations = [
        migrations.CreateModel(
            name="House",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
            bases=(model_clone.mixin.CloneMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Room",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "house",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rooms",
                        to="sample.house",
                    ),
                ),
            ],
            bases=(model_clone.mixin.CloneMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Furniture",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                (
                    "room",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="furniture",
                        to="sample.room",
                    ),
                ),
            ],
            bases=(model_clone.mixin.CloneMixin, models.Model),
        ),
    ]
