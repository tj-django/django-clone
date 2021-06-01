from django.contrib import admin

# Register your models here.
from model_clone import CloneModelAdmin
from sample.models import Author, Book, Library, Page


class PageInline(admin.StackedInline):
    model = Page
    fields = ["content"]


@admin.register(Book)
class BookAdmin(CloneModelAdmin):
    pass


@admin.register(Author)
class AuthorAdmin(CloneModelAdmin):
    list_display = ["first_name", "last_name", "sex", "age"]


@admin.register(Library)
class LibraryAdmin(CloneModelAdmin):
    model = Library
    fields = ["name", "user"]
