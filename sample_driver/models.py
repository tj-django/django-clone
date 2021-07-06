from django.db import models

from model_clone import CloneMixin


class Driver(CloneMixin, models.Model):
    name = models.CharField(max_length=255)
    age = models.SmallIntegerField()
