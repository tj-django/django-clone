from django.contrib import admin

# Register your models here.

from model_clone import CloneModelAdmin
from sample.models import Book, Author


@admin.register(Book)
class ModelToCloneAdmin(CloneModelAdmin):
    pass


@admin.register(Author)
class ModelToCloneAdmin(CloneModelAdmin):
    pass
