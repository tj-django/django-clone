from django.db import models

from model_clone import CloneMixin


class DriverFlag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Driver(CloneMixin, models.Model):
    name = models.CharField(max_length=255)
    age = models.SmallIntegerField()
    flags = models.ManyToManyField(DriverFlag)

    _clone_linked_m2m_fields = ["flags"]
