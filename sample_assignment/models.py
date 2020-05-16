from django.db import models

from model_clone import CloneMixin


class Contract(CloneMixin, models.Model):
    title = models.CharField(max_length=255)
