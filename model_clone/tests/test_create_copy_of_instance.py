from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS, IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from model_clone import create_copy_of_instance
from sample.models import Book, Library

User = get_user_model()


class CreateCopyOfInstanceTestCase(TestCase):
    REPLICA_DB_ALIAS = "replica"
    databases = {
        "default",
        "replica",
    }

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user 1")
        cls.user2 = User.objects.create(username="user 2")

    def test_cloning_model_with_custom_id(self):
        instance = Library.objects.create(name="First library", user=self.user1)
        clone = create_copy_of_instance(instance, attrs={"user": self.user2})

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertEqual(clone.user, self.user2)

    def test_cloning_model_with_a_different_db_alias_is_valid(self):
        new_user = User(username="new user 1")
        new_user.save(using=self.REPLICA_DB_ALIAS)
        instance = Library(name="First library", user=self.user1)
        instance.save(using=DEFAULT_DB_ALIAS)
        clone = create_copy_of_instance(
            instance, attrs={"user": new_user}, using=self.REPLICA_DB_ALIAS
        )

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertEqual(clone.user, new_user)
        self.assertNotEqual(instance._state.db, clone._state.db)

    def test_cloning_unique_fk_field_without_a_fallback_value_is_invalid(self):
        name = "New Library"
        instance = Library.objects.create(name=name, user=self.user1)

        with self.assertRaises(ValidationError):
            create_copy_of_instance(instance)

    def test_cloning_excluded_field_without_a_fallback_value_is_invalid(self):
        name = "New Library"
        instance = Book.objects.create(
            name=name, created_by=self.user1, slug=slugify(name)
        )

        with self.assertRaises(IntegrityError):
            create_copy_of_instance(
                instance, exclude={"slug"}, attrs={"created_by": self.user2}
            )

    def test_raises_error_when_create_copy_of_instance_uses_an_invalid_attrs_value(
        self,
    ):
        instance = Library.objects.create(name="First library", user=self.user1)

        with self.assertRaises(ValueError):
            create_copy_of_instance(instance, attrs="user")

    def test_cloning_an_invalid_object_is_invalid(self):
        class InvalidObj:
            def __init__(self):
                pass

        instance = InvalidObj()

        with self.assertRaises(ValueError):
            create_copy_of_instance(instance, attrs={"created_by": self.user2})
