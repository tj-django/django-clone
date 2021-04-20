import datetime
import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.transaction import TransactionManagementError
from django.test import TestCase, TransactionTestCase
from django.utils.text import slugify
from django.utils.timezone import make_naive
from mock import patch, PropertyMock

from sample.models import (
    Edition,
    Library,
    Book,
    Author,
    Page,
    House,
    Room,
    Furniture,
    Cover,
    BackCover,
)

User = get_user_model()


class CloneMixinTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user 1")
        cls.user2 = User.objects.create(username="user 2")

    def test_cloning_a_transient_instance_with_pk_is_invalid(self):
        instance = Library()

        with self.assertRaises(ValidationError):
            instance.make_clone()

    def test_cloning_a_transient_instance_is_invalid(self):
        instance = Book()

        with self.assertRaises(ValidationError):
            instance.make_clone()

    def test_cloning_model_with_custom_id(self):
        instance = Library.objects.create(name="First library", user=self.user1)
        clone = instance.make_clone({"user": self.user2})
        self.assertNotEqual(instance.pk, clone.pk)

    @patch("sample.models.Book._clone_excluded_fields", new_callable=PropertyMock)
    def test_cloning_model_with_excluded_fields(self, _clone_excluded_fields_mock):
        _clone_excluded_fields_mock.return_value = ["name"]
        instance = Library.objects.create(name="First library", user=self.user1)
        clone = instance.make_clone({"name": "New Library"})
        self.assertNotEqual(instance.pk, clone.pk)

    def test_cloning_explict_fields(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        clone = instance.make_clone({"user": self.user2, "name": "New name"})

        self.assertEqual(instance.name, name)
        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

    def test_cloning_unique_fk_field(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        clone = instance.make_clone({"user": self.user2})

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.user, clone.user)

    def test_cloning_unique_o2o_field_without_a_fallback_value_is_valid(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        clone = instance.make_clone()

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.user.pk, clone.user.pk)

    def test_cloning_related_unique_o2o_field_without_a_fallback_value_is_valid(self):
        with patch(
            "sample.models.Cover._clone_o2o_fields", PropertyMock(return_value=["book"])
        ):
            book = Book.objects.create(
                name="New Book 1", created_by=self.user1, slug=slugify("New Book 1")
            )
            cover = Cover.objects.create(content="New Cover", book=book)
            clone = cover.make_clone()

            self.assertNotEqual(cover.pk, clone.pk)
            self.assertNotEqual(cover.book.pk, clone.book.pk)
            self.assertEqual(cover.content, clone.content)

        with patch(
            "sample.models.Book._clone_o2o_fields",
            PropertyMock(return_value=["cover", "backcover"]),
        ):
            book = Book.objects.create(
                name="New Book 2", created_by=self.user1, slug=slugify("New Book 2")
            )
            cover = Cover.objects.create(content="New Cover", book=book)
            clone = book.make_clone()

            self.assertNotEqual(book.pk, clone.pk)
            self.assertNotEqual(cover.pk, clone.cover.pk)
            self.assertEqual(cover.content, clone.cover.content)

            book = Book.objects.create(
                name="New Book 3", created_by=self.user1, slug=slugify("New Book 3")
            )
            backcover = BackCover.objects.create(content="New Back Cover", book=book)
            clone = book.make_clone()

            self.assertNotEqual(book.pk, clone.pk)
            self.assertNotEqual(backcover.pk, clone.backcover.pk)
            self.assertEqual(backcover.content, clone.backcover.content)

    def test_cloning_with_field_overridden(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        new_name = "My New Library"
        clone = instance.make_clone(attrs={"name": new_name, "user": self.user2})

        self.assertEqual(instance.name, name)

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

        self.assertEqual(clone.name, new_name)

    def test_cloning_using_auto_now_field_is_updated(self):
        name = "New Book"
        instance = Book.objects.create(
            name=name, created_by=self.user1, slug=slugify(name)
        )
        time.sleep(1)
        new_name = "My New Book"
        clone = instance.make_clone(attrs={"name": new_name})

        self.assertEqual(instance.name, name)
        self.assertEqual(clone.created_by, instance.created_by)

        instance_created_at_total_seconds = (
            make_naive(instance.created_at) - datetime.datetime(1970, 1, 1)
        ).total_seconds()

        clone_created_at_total_seconds = (
            make_naive(clone.created_at) - datetime.datetime(1970, 1, 1)
        ).total_seconds()

        self.assertNotEqual(
            instance_created_at_total_seconds,
            clone_created_at_total_seconds,
        )

    def test_cloning_without_explicit_clone_m2m_fields(self):
        author_1 = Author.objects.create(
            first_name="Ruby", last_name="Jack", age=26, sex="F", created_by=self.user1
        )

        author_2 = Author.objects.create(
            first_name="Ibinabo",
            last_name="Jack",
            age=19,
            sex="F",
            created_by=self.user1,
        )

        name = "New Book"
        book = Book.objects.create(name=name, created_by=self.user1, slug=slugify(name))

        book.authors.set([author_1, author_2])

        book_clone = book.make_clone()

        self.assertEqual(book.name, name)
        self.assertEqual(book.created_by, book_clone.created_by)
        self.assertNotEqual(
            list(book.authors.values_list("first_name", "last_name")),
            list(book_clone.authors.values_list("first_name", "last_name")),
        )

    @patch("sample.models.Book._clone_m2m_fields", new_callable=PropertyMock)
    def test_cloning_with_explicit_clone_m2m_fields(
        self,
        _clone_m2m_fields_mock,
    ):
        author_1 = Author.objects.create(
            first_name="Opubo", last_name="Jack", age=24, sex="M", created_by=self.user1
        )

        author_2 = Author.objects.create(
            first_name="Nimabo",
            last_name="Jack",
            age=16,
            sex="M",
            created_by=self.user1,
        )
        _clone_m2m_fields_mock.return_value = ["authors"]

        book = Book.objects.create(
            name="New Book", created_by=self.user1, slug=slugify("New Book")
        )
        book.authors.set([author_1, author_2])

        book_clone = book.make_clone()

        self.assertEqual(
            list(book.authors.values_list("first_name", "last_name")),
            list(book_clone.authors.values_list("first_name", "last_name")),
        )

    @patch("sample.models.Author._clone_excluded_fields", new_callable=PropertyMock)
    def test_cloning_with_clone_excluded_fields(
        self,
        _clone_excluded_fields_mock,
    ):
        author = Author.objects.create(
            first_name="Opubo", last_name="Jack", age=24, sex="M", created_by=self.user1
        )
        _clone_excluded_fields_mock.return_value = ["last_name"]

        author_clone = author.make_clone()

        self.assertNotEqual(author.last_name, author_clone.last_name)

    @patch("sample.models.Author._clone_m2m_fields", new_callable=PropertyMock)
    def test_cloning_with_explicit_related_clone_m2m_fields(
        self,
        _clone_m2m_fields_mock,
    ):
        author = Author.objects.create(
            first_name="Opubo", last_name="Jack", age=24, sex="M", created_by=self.user1
        )

        _clone_m2m_fields_mock.return_value = ["books"]

        book_1 = Book.objects.create(
            name="New Book 1", created_by=self.user1, slug=slugify("New Book 1")
        )
        book_2 = Book.objects.create(
            name="New Book 2", created_by=self.user1, slug=slugify("New Book 2")
        )
        author.books.set([book_1, book_2])

        author_clone = author.make_clone()

        self.assertEqual(
            list(author.books.values_list("name")),
            list(author_clone.books.values_list("name")),
        )
        _clone_m2m_fields_mock.assert_called()

    def test_cloning_unique_fields_is_valid(self):
        first_name = "Ruby"
        author = Author.objects.create(
            first_name=first_name,
            last_name="Jack",
            age=26,
            sex="F",
            created_by=self.user1,
        )

        author_clone = author.make_clone()

        self.assertNotEqual(author.pk, author_clone.pk)
        self.assertEqual(
            author_clone.first_name,
            "{} {} {}".format(first_name, Author.UNIQUE_DUPLICATE_SUFFIX, 1),
        )

    @patch(
        "sample.models.Author.USE_UNIQUE_DUPLICATE_SUFFIX", new_callable=PropertyMock
    )
    def test_cloning_unique_field_with_use_unique_duplicate_suffix_set_to_False(
        self,
        use_unique_duplicate_suffix_mock,
    ):
        use_unique_duplicate_suffix_mock.return_value = False
        first_name = "Ruby"

        author = Author.objects.create(
            first_name=first_name,
            last_name="Jack",
            age=26,
            sex="F",
            created_by=self.user1,
        )
        with self.assertRaises(ValidationError):
            author.make_clone()

        use_unique_duplicate_suffix_mock.assert_called()

    @patch("sample.models.Author.UNIQUE_DUPLICATE_SUFFIX", new_callable=PropertyMock)
    def test_cloning_unique_field_with_a_custom_unique_duplicate_suffix(
        self,
        unique_duplicate_suffix_mock,
    ):
        unique_duplicate_suffix_mock.return_value = "new"
        first_name = "Ruby"

        author = Author.objects.create(
            first_name=first_name,
            last_name="Jack",
            age=26,
            sex="F",
            created_by=self.user1,
        )

        author_clone = author.make_clone()

        self.assertNotEqual(author.pk, author_clone.pk)
        self.assertEqual(
            author_clone.first_name,
            "{} {} {}".format(first_name, "new", 1),
        )

    def test_cloning_unique_together_fields_with_enum_field(self):
        first_name = "Ruby"
        last_name = "Jack"

        author = Author.objects.create(
            first_name=first_name,
            last_name=last_name,
            age=26,
            sex="F",
            created_by=self.user1,
        )

        author_clone = author.make_clone()

        self.assertNotEqual(author.pk, author_clone.pk)
        self.assertEqual(author.sex, author_clone.sex)
        self.assertEqual(
            author_clone.first_name,
            "{} {} {}".format(first_name, Author.UNIQUE_DUPLICATE_SUFFIX, 1),
        )
        self.assertEqual(
            author_clone.last_name,
            "{} {} {}".format(last_name, Author.UNIQUE_DUPLICATE_SUFFIX, 1),
        )

    def test_cloning_unique_slug_field(self):
        name = "New Book"
        book = Book.objects.create(name=name, created_by=self.user1, slug=slugify(name))

        book_clone = book.make_clone()

        self.assertEqual(
            book_clone.slug,
            slugify("{} {} {}".format(book.slug, Book.UNIQUE_DUPLICATE_SUFFIX, 1)),
        )

    def test_making_sub_clones_of_a_unique_slug_field(self):
        name = "New Book"
        book = Book.objects.create(name=name, created_by=self.user1, slug=slugify(name))

        book_clone = book.make_clone()

        self.assertEqual(
            book_clone.slug,
            slugify("{} {} {}".format(book.slug, Book.UNIQUE_DUPLICATE_SUFFIX, 1)),
        )

        for i in range(2, 7):
            book_clone = book_clone.make_clone()

            self.assertEqual(
                book_clone.slug,
                slugify("{} {} {}".format(book.slug, Book.UNIQUE_DUPLICATE_SUFFIX, i)),
            )

    def test_cloning_unique_fields_max_length(self):
        """
        Max unique field length handling.

        Set the initial value for the unique field to max length
        and test to append the [ copy count]
        """
        first_name = (
            "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, "
            "sed diam nonumy eirmod tempor invidunt ut labore et dolore "
            "magna aliquyam erat, sed diam voluptua. At vero eos et accusam "
            "et justo duo dolores "
        )
        author = Author.objects.create(
            first_name=first_name,
            last_name="Jack",
            age=26,
            sex="F",
            created_by=self.user1,
        )

        author_clone = author.make_clone()

        self.assertEqual(
            len(author_clone.first_name),
            Author._meta.get_field("first_name").max_length,
        )
        self.assertNotEqual(author.pk, author_clone.pk)
        self.assertEqual(
            author_clone.first_name,
            "{} {} {}".format(first_name[:193], Author.UNIQUE_DUPLICATE_SUFFIX, 1),
        )

    def test_cloning_instances_in_an_atomic_transaction_with_auto_commit_on_raises_errors(
        self,
    ):
        first_name = (
            "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, "
            "sed diam nonumy eirmod tempor invidunt ut labore et dolore "
            "magna aliquyam erat, sed diam voluptua. At vero eos et accusam "
            "et justo duo dolores "
        )
        author = Author.objects.create(
            first_name=first_name,
            last_name="Jack",
            age=26,
            sex="F",
            created_by=self.user1,
        )

        with self.assertRaises(TransactionManagementError):
            author.bulk_clone(1000, auto_commit=True)

    @patch(
        "sample.models.Book.MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS",
        new_callable=PropertyMock,
    )
    def test_bulk_cloning_instances_that_exceed_the_max_unique_count_raises_an_error(
        self,
        max_unique_query_attempts_mock,
    ):
        class InvalidNumber(object):
            """
            Return False for a number that should always be less than the compared value.
            """

            def __init__(self, val):
                self.__val = val

            def __get__(self, instance, owner):
                return self.__val

            def __lt__(self, other):
                return False

            def __gt__(self, other):
                return self.__val > other

            def __ge__(self, other):
                return self.__val > other

        max_unique_query_attempts_mock.return_value = InvalidNumber(100)
        name = "New Book"
        book = Book.objects.create(name=name, created_by=self.user1, slug=slugify(name))

        with self.assertRaises(AssertionError):
            book.bulk_clone(1000)

    def test_cloning_instances_in_an_atomic_transaction_with_auto_commit_off_is_valid(
        self,
    ):
        first_name = (
            "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, "
            "sed diam nonumy eirmod tempor invidunt ut labore et dolore "
            "magna aliquyam erat, sed diam voluptua. At vero eos et accusam "
            "et justo duo dolores "
        )
        author = Author.objects.create(
            first_name=first_name,
            last_name="Jack",
            age=26,
            sex="F",
            created_by=self.user1,
        )

        clones = author.bulk_clone(1000)

        self.assertEqual(len(clones), 1000)

        for clone in clones:
            self.assertNotEqual(author.pk, clone.pk)
            self.assertRegexpMatches(
                clone.first_name,
                r"{}\s[\d]".format(Author.UNIQUE_DUPLICATE_SUFFIX),
            )

    @patch(
        "sample.models.Book._clone_m2o_or_o2m_fields",
        new_callable=PropertyMock,
    )
    def test_cloning_one_to_many(
        self,
        _clone_m2o_or_o2m_fields_mock,
    ):
        _clone_m2o_or_o2m_fields_mock.return_value = ["page_set"]

        name = "New Book"
        book = Book.objects.create(name=name, created_by=self.user1, slug=slugify(name))

        page_1 = Page.objects.create(content="Page 1 content", book=book)
        page_2 = Page.objects.create(content="Page 2 content", book=book)
        book.page_set.set([page_1, page_2])

        Edition.objects.create(seq=1, book=book)
        self.assertEqual(self.user1.book_set.count(), 1)

        book_clone = book.make_clone()

        self.assertEqual(book.name, name)
        self.assertEqual(book_clone.name, name)
        self.assertEqual(
            list(book.page_set.values_list("content")),
            list(book_clone.page_set.values_list("content")),
        )
        self.assertNotEqual(
            list(book.page_set.values_list("id")),
            list(book_clone.page_set.values_list("id")),
        )
        self.assertNotEqual(book.editions.count(), book_clone.editions.count())
        self.assertEqual(self.user1.book_set.count(), 2)
        _clone_m2o_or_o2m_fields_mock.assert_called()

    @patch(
        "sample.models.Edition._clone_m2o_or_o2m_fields",
        new_callable=PropertyMock,
    )
    def test_cloning_many_to_one(
        self,
        _clone_m2o_or_o2m_fields_mock,
    ):
        _clone_m2o_or_o2m_fields_mock.return_value = ["book"]

        name = "New Book"
        book = Book.objects.create(name=name, created_by=self.user1, slug=slugify(name))
        page = Page.objects.create(content="Page 1 content", book=book)
        edition = Edition.objects.create(seq=1, book=book)

        book.page_set.set([page])
        edition_clone = edition.make_clone()

        self.assertNotEqual(edition.book.id, edition_clone.book.id)
        self.assertEqual(edition.book.name, edition_clone.book.name)
        _clone_m2o_or_o2m_fields_mock.assert_called()

    def test_cloning_complex_model_relationships(self):
        house = House.objects.create(name="My House")

        room_1 = Room.objects.create(name="Room 1 in house", house=house)
        room_2 = Room.objects.create(name="Room 2 in house", house=house)

        Furniture.objects.create(name="Chair for room 1", room=room_1)
        Furniture.objects.create(name="Chair for room 2", room=room_2)

        clone_house = house.make_clone()

        self.assertEqual(house.name, clone_house.name)
        self.assertEqual(house.rooms.count(), clone_house.rooms.count())


class CloneMixinTransactionTestCase(TransactionTestCase):
    def test_cloning_multiple_instances_doesnt_exceed_the_max_length(self):
        user = User.objects.create()
        first_name = (
            "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, "
            "sed diam nonumy eirmod tempor invidunt ut labore et dolore "
            "magna aliquyam erat, sed diam voluptua. At vero eos et accusam "
            "et justo duo dolores "
        )
        author = Author.objects.create(
            first_name=first_name, last_name="Jack", age=26, sex="F", created_by=user
        )

        clones = author.bulk_clone(1000)

        self.assertEqual(len(clones), 1000)

        for clone in clones:
            self.assertNotEqual(author.pk, clone.pk)
            self.assertRegexpMatches(
                clone.first_name,
                r"{}\s[\d]".format(Author.UNIQUE_DUPLICATE_SUFFIX),
            )

    def test_cloning_multiple_instances_with_autocommit_is_valid(self):
        user = User.objects.create()
        first_name = (
            "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, "
            "sed diam nonumy eirmod tempor invidunt ut labore et dolore "
            "magna aliquyam erat, sed diam voluptua. At vero eos et accusam "
            "et justo duo dolores 2"
        )
        author = Author.objects.create(
            first_name=first_name, last_name="Jack", age=26, sex="F", created_by=user
        )

        clones = author.bulk_clone(1000, auto_commit=True)

        self.assertEqual(len(clones), 1000)

        for clone in clones:
            self.assertNotEqual(author.pk, clone.pk)
            self.assertRegexpMatches(
                clone.first_name,
                r"{}\s[\d]".format(Author.UNIQUE_DUPLICATE_SUFFIX),
            )
