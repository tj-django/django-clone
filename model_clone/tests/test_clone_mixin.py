import datetime
import time

from django.contrib.auth import get_user_model
from django.core.checks import Error
from django.core.exceptions import ValidationError
from django.db.transaction import TransactionManagementError
from django.db.utils import DEFAULT_DB_ALIAS, IntegrityError
from django.test import TestCase, TransactionTestCase
from django.utils.text import slugify
from django.utils.timezone import make_naive
from mock import PropertyMock, patch

from model_clone.apps import ModelCloneConfig
from sample.models import (
    Author,
    BackCover,
    Book,
    BookSaleTag,
    BookTag,
    Cover,
    Edition,
    Ending,
    Furniture,
    House,
    Library,
    Page,
    Product,
    Room,
    SaleTag,
    Sentence,
    Tag,
)

User = get_user_model()


class CloneMixinTestCase(TestCase):
    REPLICA_DB_ALIAS = "replica"
    databases = {
        "default",
        "replica",
    }

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user 1")
        cls.user2 = User.objects.create(username="user 2")

    def test_cloning_a_transient_instance_with_pk_is_invalid(self):
        instance = Library()

        with self.assertRaises(IntegrityError):
            instance.make_clone()

    def test_cloning_a_transient_instance_is_invalid(self):
        instance = Book()

        with self.assertRaises(ValidationError):
            instance.make_clone()

    def test_cloning_model_with_custom_id(self):
        instance = Library.objects.create(name="First library", user=self.user1)
        clone = instance.make_clone({"user": self.user2})
        self.assertNotEqual(instance.pk, clone.pk)

    @patch("sample.models.Library._clone_excluded_fields", new_callable=PropertyMock)
    def test_cloning_model_with_excluded_fields(self, _clone_excluded_fields_mock):
        _clone_excluded_fields_mock.return_value = ["name"]
        instance = Library.objects.create(name="First library", user=self.user1)
        clone = instance.make_clone({"name": "New Library"})
        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

    def test_cloning_explict_fields(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        clone = instance.make_clone({"user": self.user2, "name": "New name"})

        self.assertEqual(instance.name, name)
        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

    @patch("sample.models.Book._clone_fields", new_callable=PropertyMock)
    def test_cloning_with_default_value(self, _clone_fields_mock):
        instance = Book.objects.create(
            name="Not Published Book", created_by=self.user1, published_at=None
        )
        _clone_fields_mock.return_value = ["name", "created_by", "slug", "published_at"]
        clone = instance.make_clone()
        self.assertNotEqual(instance.pk, clone.pk)
        self.assertEqual(instance.name, clone.name)
        self.assertNotEqual(instance.slug, clone.slug)
        self.assertIsNone(clone.published_at)

        _clone_fields_mock.return_value.remove("published_at")
        clone = instance.make_clone()
        self.assertNotEqual(instance.pk, clone.pk)
        self.assertEqual(instance.name, clone.name)
        self.assertNotEqual(instance.slug, clone.slug)
        self.assertIsNotNone(clone.published_at)

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
            self.assertIsNotNone(clone.backcover.pk)
            self.assertNotEqual(backcover.pk, clone.backcover.pk)
            self.assertEqual(backcover.content, clone.backcover.content)

    def test_cloning_model_with_a_different_db_alias_is_valid(self):
        name = "New Library"
        instance = Library(name=name, user=self.user1)
        instance.save(using=DEFAULT_DB_ALIAS)
        new_user = User(username="new user 2")
        new_user.save(using=self.REPLICA_DB_ALIAS)
        clone = instance.make_clone(
            attrs={"user": new_user, "name": "New name"},
            using=self.REPLICA_DB_ALIAS,
        )

        self.assertEqual(instance.name, name)
        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

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

    def test_cloning_with_unique_constraint_is_valid(self):
        sale_tag = SaleTag.objects.create(name="test-sale-tag")
        clone_sale_tag_1 = sale_tag.make_clone()

        self.assertNotEqual(sale_tag.pk, clone_sale_tag_1.pk)
        self.assertRegexpMatches(
            clone_sale_tag_1.name,
            r"{}\s[\d]".format(SaleTag.UNIQUE_DUPLICATE_SUFFIX),
        )

        clone_sale_tag_2 = clone_sale_tag_1.make_clone()

        self.assertNotEqual(clone_sale_tag_1.pk, clone_sale_tag_2.pk)
        self.assertRegexpMatches(
            clone_sale_tag_2.name,
            r"{}\s[\d]".format(SaleTag.UNIQUE_DUPLICATE_SUFFIX),
        )

    def test_cloning_with_unique_constraint_uses_field_default(self):
        tag = Tag.objects.create(name="test-tag")
        clone_tag = tag.make_clone()

        self.assertNotEqual(tag.pk, clone_tag.pk)
        self.assertRegexpMatches(
            clone_tag.name,
            r"\s[\d]",
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

        book_1 = Book.objects.create(
            name="New Book 1", created_by=self.user1, slug=slugify("New Book 1")
        )
        book_1.authors.set([author_1, author_2])

        book_clone_1 = book_1.make_clone()

        self.assertEqual(
            list(book_1.authors.values_list("first_name", "last_name")),
            list(book_clone_1.authors.values_list("first_name", "last_name")),
        )

        tag_1 = Tag.objects.create(name="test-tag-1")
        tag_2 = Tag.objects.create(name="test-tag-2")

        _clone_m2m_fields_mock.return_value = ["tags"]

        book_2 = Book.objects.create(
            name="New Book 2", created_by=self.user1, slug=slugify("New Book 2")
        )
        BookTag.objects.create(book=book_2, tag=tag_1)
        BookTag.objects.create(book=book_2, tag=tag_2)

        book_clone_2 = book_2.make_clone()

        self.assertEqual(
            list(book_2.tags.values_list("name")),
            list(book_clone_2.tags.values_list("name")),
        )

        sale_tag_1 = SaleTag.objects.create(name="test-tag-3")
        sale_tag_2 = SaleTag.objects.create(name="test-tag-4")

        _clone_m2m_fields_mock.return_value = ["sale_tags"]

        book_3 = Book.objects.create(
            name="New Book 3", created_by=self.user1, slug=slugify("New Book 3")
        )
        BookSaleTag.objects.create(book=book_3, sale_tag=sale_tag_1)
        BookSaleTag.objects.create(book=book_3, sale_tag=sale_tag_2)

        book_clone_3 = book_3.make_clone()

        self.assertEqual(
            list(book_3.sale_tags.values_list("name")),
            list(book_clone_3.sale_tags.values_list("name")),
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
        with self.assertRaises(IntegrityError):
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

        author_clone_1 = author.make_clone()

        self.assertNotEqual(author.pk, author_clone_1.pk)
        self.assertEqual(author.sex, author_clone_1.sex)
        self.assertEqual(
            author_clone_1.first_name,
            "{} {} {}".format(first_name, Author.UNIQUE_DUPLICATE_SUFFIX, 1),
        )
        self.assertEqual(
            author_clone_1.last_name,
            Author._meta.get_field("last_name").get_default(),
        )

        author_clone_2 = author.make_clone()

        self.assertNotEqual(author.pk, author_clone_2.pk)
        self.assertEqual(author.sex, author_clone_2.sex)
        self.assertEqual(
            author_clone_2.first_name,
            "{} {} {}".format(first_name, Author.UNIQUE_DUPLICATE_SUFFIX, 2),
        )
        self.assertEqual(
            author_clone_2.last_name,
            "{} {} {}".format(
                Author._meta.get_field("last_name").get_default(),
                Author.UNIQUE_DUPLICATE_SUFFIX,
                1,
            ),
        )

        author_clone_3 = author.make_clone()

        self.assertNotEqual(author.pk, author_clone_3.pk)
        self.assertEqual(author.sex, author_clone_3.sex)
        self.assertEqual(
            author_clone_3.first_name,
            "{} {} {}".format(first_name, Author.UNIQUE_DUPLICATE_SUFFIX, 3),
        )
        self.assertEqual(
            author_clone_3.last_name,
            "{} {} {}".format(
                Author._meta.get_field("last_name").get_default(),
                Author.UNIQUE_DUPLICATE_SUFFIX,
                2,
            ),
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

    @patch(
        "sample.models.Book.USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS",
        new_callable=PropertyMock,
    )
    def test_making_sub_clones_of_a_non_unique_slug_field_appends_copy(
        self,
        use_duplicate_suffix_for_non_unique_fields_mock,
    ):
        name = "New Book"
        book = Book.objects.create(
            name=name,
            created_by=self.user1,
            slug=slugify(name),
            custom_slug=slugify(name),
        )

        use_duplicate_suffix_for_non_unique_fields_mock.return_value = True

        book_clone = book.make_clone()

        self.assertEqual(
            book_clone.custom_slug,
            slugify("{} {}".format(book.custom_slug, Book.DUPLICATE_SUFFIX)),
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

    @patch(
        "sample.models.Edition.USE_UNIQUE_DUPLICATE_SUFFIX",
        new_callable=PropertyMock,
    )
    @patch(
        "sample.models.Edition.UNIQUE_DUPLICATE_SUFFIX",
        new_callable=PropertyMock,
    )
    def test_unique_duplicate_suffix_check(
        self, unique_duplicate_suffix_mock, use_unique_duplicate_suffix_mock
    ):
        use_unique_duplicate_suffix_mock.return_value = True
        unique_duplicate_suffix_mock.return_value = ""

        errors = Edition.check()
        expected_errors = [
            Error(
                "UNIQUE_DUPLICATE_SUFFIX is required.",
                hint=(
                    "Please provide UNIQUE_DUPLICATE_SUFFIX"
                    + " for {} or set USE_UNIQUE_DUPLICATE_SUFFIX=False".format(
                        Edition.__name__,
                    )
                ),
                obj=Edition,
                id="{}.E001".format(ModelCloneConfig.name),
            )
        ]
        self.assertEqual(errors, expected_errors)

    @patch(
        "sample.models.Edition._clone_fields",
        new_callable=PropertyMock,
    )
    @patch(
        "sample.models.Edition._clone_excluded_fields",
        new_callable=PropertyMock,
    )
    def test_clone_fields_check(self, _clone_excluded_fields_mock, _clone_fields_mock):
        _clone_excluded_fields_mock.return_value = ["test"]
        _clone_fields_mock.return_value = ["test"]

        errors = Edition.check()
        expected_errors = [
            Error(
                "Conflicting configuration.",
                hint=(
                    'Please provide either "_clone_fields"'
                    + ' or "_clone_excluded_fields" for model {}'.format(
                        Edition.__name__,
                    )
                ),
                obj=Edition,
                id="{}.E002".format(ModelCloneConfig.name),
            )
        ]
        self.assertEqual(errors, expected_errors)

    @patch(
        "sample.models.Edition._clone_m2m_fields",
        new_callable=PropertyMock,
    )
    @patch(
        "sample.models.Edition._clone_excluded_m2m_fields",
        new_callable=PropertyMock,
    )
    def test_clone_m2m_fields_check(
        self, _clone_m2m_fields_mock, _clone_excluded_m2m_fields_mock
    ):
        _clone_m2m_fields_mock.return_value = ["test"]
        _clone_excluded_m2m_fields_mock.return_value = ["test"]

        errors = Edition.check()
        expected_errors = [
            Error(
                "Conflicting configuration.",
                hint=(
                    'Please provide either "_clone_m2m_fields"'
                    + ' or "_clone_excluded_m2m_fields" for model {}'.format(
                        Edition.__name__,
                    )
                ),
                obj=Edition,
                id="{}.E002".format(ModelCloneConfig.name),
            )
        ]
        self.assertEqual(errors, expected_errors)

    @patch(
        "sample.models.Edition._clone_m2o_or_o2m_fields",
        new_callable=PropertyMock,
    )
    @patch(
        "sample.models.Edition._clone_excluded_m2o_or_o2m_fields",
        new_callable=PropertyMock,
    )
    def test_clone_m2o_or_o2m_fields_check(
        self, _clone_m2o_or_o2m_fields_mock, _clone_excluded_m2o_or_o2m_fields_mock
    ):
        _clone_m2o_or_o2m_fields_mock.return_value = ["test"]
        _clone_excluded_m2o_or_o2m_fields_mock.return_value = ["test"]

        errors = Edition.check()
        expected_errors = [
            Error(
                "Conflicting configuration.",
                hint=(
                    'Please provide either "_clone_m2o_or_o2m_fields"'
                    + ' or "_clone_excluded_m2o_or_o2m_fields" for model {}'.format(
                        Edition.__name__,
                    )
                ),
                obj=Edition,
                id="{}.E002".format(ModelCloneConfig.name),
            )
        ]
        self.assertEqual(errors, expected_errors)

    @patch(
        "sample.models.Edition._clone_o2o_fields",
        new_callable=PropertyMock,
    )
    @patch(
        "sample.models.Edition._clone_excluded_o2o_fields",
        new_callable=PropertyMock,
    )
    def test_clone_o2o_fields_check(
        self, _clone_o2o_fields_mock, _clone_excluded_o2o_fields_mock
    ):
        _clone_o2o_fields_mock.return_value = ["test"]
        _clone_excluded_o2o_fields_mock.return_value = ["test"]

        errors = Edition.check()
        expected_errors = [
            Error(
                "Conflicting configuration.",
                hint=(
                    'Please provide either "_clone_o2o_fields"'
                    + ' or "_clone_excluded_o2o_fields" for model {}'.format(
                        Edition.__name__,
                    )
                ),
                obj=Edition,
                id="{}.E002".format(ModelCloneConfig.name),
            )
        ]
        self.assertEqual(errors, expected_errors)

    def test_cloning_o2o_fields(self):
        sentence = Sentence.objects.create(value="A really long sentence")
        Ending.objects.create(sentence=sentence)

        self.assertEqual(1, Sentence.objects.count())
        self.assertEqual(1, Ending.objects.count())

        clones = [sentence.make_clone() for _ in range(2)]

        self.assertEqual(2, len(clones))
        self.assertEqual(3, Sentence.objects.count())


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

    def test_cloning_model_with_unique_text_field(self):
        product = Product.objects.create(name="Test Product")
        clone = product.make_clone()
        self.assertEqual(
            clone.name,
            "{0} {1} 1".format(product.name, Product.UNIQUE_DUPLICATE_SUFFIX),
        )
