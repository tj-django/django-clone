from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from mock import patch, PropertyMock

from sample.models import Library, Book, Author

User = get_user_model()


class CloneMixinTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create()

    def test_cloning_model_with_custom_id(self):
        instance = Library.objects.create(name='First library')
        clone = instance.make_clone()
        self.assertNotEqual(instance.pk, clone.pk)

    def test_cloning_explict_fields(self):
        name = 'New Library'
        instance = Library.objects.create(name=name)
        clone = instance.make_clone()

        self.assertEqual(instance.name, name)

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

    def test_cloning_with_field_overriden(self):
        name = 'New Library'
        instance = Library.objects.create(name=name)
        new_name = 'My New Library'
        clone = instance.make_clone(attrs={'name': new_name})

        self.assertEqual(instance.name, name)

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertNotEqual(instance.name, clone.name)

        self.assertEqual(clone.name, new_name)

    def test_cloning_using_auto_now_field_is_updated(self):
        name = 'New Book'
        instance = Book.objects.create(name=name, created_by=self.user)
        new_name = 'My New Book'
        clone = instance.make_clone(attrs={'name': new_name})

        self.assertEqual(instance.name, name)
        self.assertEqual(clone.created_by, instance.created_by)

        self.assertNotEqual(instance.created_at, clone.created_at)

    def test_cloning_without_explicit__clone_many_to_many_fields(self):
        author_1 = Author.objects.create(
            first_name='Ruby',
            last_name='Jack',
            age=26,
            sex='F',
            created_by=self.user
        )

        author_2 = Author.objects.create(
            first_name='Ibinabo',
            last_name='Jack',
            age=19,
            sex='F',
            created_by=self.user
        )

        name = 'New Book'
        book = Book.objects.create(name=name, created_by=self.user)

        book.authors.set([author_1, author_2])

        book_clone = book.make_clone()

        self.assertEqual(book.name, name)
        self.assertEqual(book.created_by, book_clone.created_by)
        self.assertNotEqual(
            book.authors.values_list('first_name', 'last_name'),
            book_clone.authors.values_list('first_name', 'last_name'),
        )

    @patch('sample.models.Book._clone_many_to_many_fields', new_callable=PropertyMock)
    def test_cloning_with_explicit__clone_many_to_many_fields(self, _clone_many_to_many_fields_mock):
        author_1 = Author.objects.create(
            first_name='Ruby',
            last_name='Jack',
            age=26,
            sex='F',
            created_by=self.user
        )

        author_2 = Author.objects.create(
            first_name='Ibinabo',
            last_name='Jack',
            age=19,
            sex='F',
            created_by=self.user
        )

        name = 'New Book'
        _clone_many_to_many_fields_mock.return_value = ['authors']

        book = Book.objects.create(name=name, created_by=self.user)

        book.authors.set([author_1, author_2])

        book_clone = book.make_clone()

        self.assertEqual(book.name, name)
        self.assertEqual(book.created_by, book_clone.created_by)
        self.assertNotEqual(
            book.authors.values_list('first_name', 'last_name'),
            book_clone.authors.values_list('first_name', 'last_name'),
        )
        _clone_many_to_many_fields_mock.assert_called_once()

    def test_cloning_unique_fields_is_valid(self):
        first_name = 'Ruby'
        author = Author.objects.create(
            first_name=first_name,
            last_name='Jack',
            age=26,
            sex='F',
            created_by=self.user
        )

        author_clone = author.make_clone()

        self.assertNotEqual(author.pk, author_clone.pk)
        self.assertEqual(
            author_clone.first_name,
            '{} {} {}'.format(first_name, Author.UNIQUE_DUPLICATE_SUFFIX, 1),
        )

    @patch('sample.models.Author.USE_UNIQUE_DUPLICATE_SUFFIX', new_callable=PropertyMock)
    def test_cloning_unique_field_with_use_unique_duplicate_suffix_set_to_False(
        self,
        use_unique_duplicate_suffix_mock,
    ):
        use_unique_duplicate_suffix_mock.return_value = False
        first_name = 'Ruby'

        author = Author.objects.create(
            first_name=first_name,
            last_name='Jack',
            age=26,
            sex='F',
            created_by=self.user
        )
        with self.assertRaises(IntegrityError) as e:
            author.make_clone()

        use_unique_duplicate_suffix_mock.assert_called_once()

    @patch('sample.models.Author.UNIQUE_DUPLICATE_SUFFIX', new_callable=PropertyMock)
    def test_cloning_unique_field_with_a_custom_unique_duplicate_suffix(
        self,
        unique_duplicate_suffix_mock,
    ):
        unique_duplicate_suffix_mock.return_value = 'new'
        first_name = 'Ruby'

        author = Author.objects.create(
            first_name=first_name,
            last_name='Jack',
            age=26,
            sex='F',
            created_by=self.user
        )

        author_clone = author.make_clone()

        self.assertNotEqual(author.pk, author_clone.pk)
        self.assertEqual(
            author_clone.first_name,
            '{} {} {}'.format(first_name, 'new', 1),
        )

