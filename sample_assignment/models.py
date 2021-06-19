from django.db import models


class Contract(models.Model):
    title = models.CharField(max_length=255)
