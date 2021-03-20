from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.transaction import TransactionManagementError
from django.test import TestCase, TransactionTestCase
from mock import patch, PropertyMock

from sample.models import Library, Book, Author, Page

User = get_user_model()


class CloneMixinTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user 1")
        cls.user2 = User.objects.create(username="user 2")

    def test_cloning_model_with_custom_id(self):
        instance = Library.objects.create(name="First library", user=self.user1)
        clone = instance.make_clone({"user": self.user2})
        self.assertNotEqual(instance.pk, clone.pk)

    def test_cloning_explict_fields(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        clone = instance.make_clone({"user": self.user2})

        self.assertEqual(instance.name, name)

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

    def test_cloning_unique_fk_field(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        clone = instance.make_clone({"user": self.user2})

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.user, clone.user)

    def test_cloning_unique_fk_field_without_a_fallback_value_is_invalid(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)
        with self.assertRaises(IntegrityError):
            instance.make_clone()

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
        instance = Book.objects.create(name=name, created_by=self.user1)
        new_name = "My New Book"
        clone = instance.make_clone(attrs={"name": new_name})

        self.assertEqual(instance.name, name)
        self.assertEqual(clone.created_by, instance.created_by)

        self.assertNotEqual(instance.created_at, clone.created_at)

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
        book = Book.objects.create(name=name, created_by=self.user1)

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

        book = Book.objects.create(name="New Book", created_by=self.user1)
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

        book_1 = Book.objects.create(name="New Book 1", created_by=self.user1)
        book_2 = Book.objects.create(name="New Book 2", created_by=self.user1)
        author.books.set([book_1, book_2])

        author_clone = author.make_clone()

        self.assertEqual(
            list(author.books.values_list("name")),
            list(author_clone.books.values_list("name")),
        )
        _clone_m2m_fields_mock.assert_called_once()

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

    def test_cloning_unique_fields_max_length(self):
        """Max unique field length handling

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
        "sample.models.Book._clone_m2m_or_o2m_fields",
        new_callable=PropertyMock,
    )
    def test_cloning_one_to_many_many_to_one(
        self,
        _clone_m2m_or_o2m_fields_mock,
    ):
        _clone_m2m_or_o2m_fields_mock.return_value = ["pages"]

        name = "New Book"
        book = Book.objects.create(name=name, created_by=self.user1)

        page_1 = Page.objects.create(content="Page 1 content", book=book)
        page_2 = Page.objects.create(content="Page 2 content", book=book)

        book.pages.set([page_1, page_2])
        book_clone = book.make_clone()

        self.assertEqual(book.name, name)
        self.assertEqual(book_clone.name, name)
        self.assertEqual(
            list(book.pages.values_list("content")),
            list(book_clone.pages.values_list("content")),
        )
        self.assertNotEqual(
            list(book.pages.values_list("id")),
            list(book_clone.pages.values_list("id")),
        )
        _clone_m2m_or_o2m_fields_mock.assert_called_once()


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
