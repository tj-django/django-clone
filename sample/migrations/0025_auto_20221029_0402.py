# Generated by Django 3.2.16 on 2022-10-29 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sample", "0024_alter_edition_book"),
    ]

    operations = [
        migrations.CreateModel(
            name="Editor",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="book",
            name="editors",
            field=models.ManyToManyField(related_name="books", to="sample.Editor"),
        ),
    ]
