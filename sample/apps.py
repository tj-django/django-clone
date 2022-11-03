# pylint: disable=unused-import
from django.apps import AppConfig


class SampleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sample"

    def ready(self):
        from . import signals  # noqa: F401
