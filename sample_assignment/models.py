from django.db import models


class Contract(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title
