# Generated by Django 3.0 on 2019-12-03 09:47

import django.db.models.deletion
from django.db import migrations, models

import model_clone.mixin


class Migration(migrations.Migration):

    dependencies = [
        ("sample", "0004_auto_20191122_0848"),
    ]

    operations = [
        migrations.CreateModel(
            name="Page",
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
                ("content", models.CharField(max_length=20000)),
                (
                    "book",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="sample.Book",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(model_clone.mixin.CloneMixin, models.Model),
        ),
    ]
