from django.db import models

from model_clone.mixin import CloneMixin


class CloneModel(CloneMixin, models.Model):
    class Meta:
        abstract = True
