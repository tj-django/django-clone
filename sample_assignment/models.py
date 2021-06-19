from django.db import models

from model_clone import CloneMixin


class Contract(models.Model):
    title = models.CharField(max_length=255)
