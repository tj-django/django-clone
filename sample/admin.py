from django.contrib import admin

# Register your models here.
from django.forms import ALL_FIELDS

from model_clone import CloneModelAdmin
from sample.models import Book, Author


@admin.register(Book)
class BookAdmin(CloneModelAdmin):
    pass


@admin.register(Author)
class AuthorAdmin(CloneModelAdmin):
    list_display = ['first_name', 'last_name', 'sex', 'age']
