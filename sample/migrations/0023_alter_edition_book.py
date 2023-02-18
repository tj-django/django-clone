# Generated by Django 3.2.13 on 2022-06-24 13:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sample", "0022_ending_sentence"),
    ]

    operations = [
        migrations.AlterField(
            model_name="edition",
            name="book",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="editions",
                to="sample.book",
            ),
        ),
    ]