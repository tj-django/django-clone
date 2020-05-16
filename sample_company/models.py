from django.db import models

from model_clone import CloneMixin


class CompanyDepot(CloneMixin, models.Model):
    name = models.CharField(max_length=255)
