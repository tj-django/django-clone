from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify

from sample.models import Book, Edition

User = get_user_model()


class CloneSignalsTestCase(TestCase):
    REPLICA_DB_ALIAS = "replica"
    databases = {
        "default",
        "replica",
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username="user")

    def test_signals(self):
        name = "New Book"
        first_published_at = timezone.datetime(
            1970, 1, 1, tzinfo=timezone.get_default_timezone()
        )
        book = Book.objects.create(
            name=name,
            created_by=self.user,
            slug=slugify(name),
            published_at=first_published_at,
        )
        self.assertEqual(book.published_at, first_published_at)
        edition = Edition.objects.create(seq=1, book=book)
        cloned_edition = edition.make_clone()
        self.assertEqual(cloned_edition.seq, 2)
        book.refresh_from_db()
        self.assertNotEqual(book.published_at, first_published_at)
