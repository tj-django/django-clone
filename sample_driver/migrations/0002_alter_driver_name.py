# Generated by Django 3.2 on 2021-04-22 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sample_driver", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="driver",
            name="name",
            field=models.CharField(max_length=200),
        ),
    ]
