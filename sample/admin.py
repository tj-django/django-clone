from django.contrib import admin

# Register your models here.

from model_clone import ClonableModelAdmin
from sample.models import Book, Author


@admin.register(Book)
class ModelToCloneAdmin(ClonableModelAdmin):
    pass


@admin.register(Author)
class ModelToCloneAdmin(ClonableModelAdmin):
    pass
