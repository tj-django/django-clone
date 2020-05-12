from django.db import models

from model_clone.mixins.clone import CloneMixin


class CloneModel(CloneMixin, models.Model):
    class Meta:
        abstract = True
