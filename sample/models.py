from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _

from model_clone.models import CloneModel


class Author(CloneModel):
    first_name = models.CharField(max_length=200, unique=True)
    last_name = models.CharField(max_length=200)
    age = models.PositiveIntegerField()

    SEX_CHOICES = [
        ('F', 'Female'),
        ('M', 'Male'),
    ]
    sex = models.CharField(choices=SEX_CHOICES, max_length=1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return _('{} {}'.format(self.first_name, self.last_name))


class Book(CloneModel):
    name = models.CharField(max_length=2000)
    authors = models.ManyToManyField(Author, related_name='books')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return _(self.name)


class Page(CloneModel):
    content = models.CharField(max_length=20000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='pages')


class Library(CloneModel):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)

    _clone_model_fields = ['id']

    def __str__(self):
        return _(self.name)
