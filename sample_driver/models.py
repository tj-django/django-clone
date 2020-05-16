from django.db import models

from model_clone import CloneMixin


class Driver(models.Model, CloneMixin):
    name = models.CharField(max_length=255)
    age = models.SmallIntegerField()
