# Generated by Django 3.1.8 on 2021-06-28 23:01

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("sample", "0017_auto_20210624_1117"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="last_name",
            field=models.CharField(blank=True, default="Unknown", max_length=200),
        ),
        migrations.AlterField(
            model_name="author",
            name="sex",
            field=models.CharField(
                choices=[("U", "Unknown"), ("F", "Female"), ("M", "Male")],
                default="U",
                max_length=1,
            ),
        ),
        migrations.AddField(
            model_name="book",
            name="published_at",
            field=models.DateTimeField(blank=True, default=timezone.now, null=True),
        ),
    ]
