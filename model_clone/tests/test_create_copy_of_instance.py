from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils.text import slugify

from model_clone import create_copy_of_instance
from sample.models import Library, Book

User = get_user_model()


class CreateCopyOfInstanceTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username="user 1")
        cls.user2 = User.objects.create(username="user 2")

    def test_cloning_model_with_custom_id(self):
        instance = Library.objects.create(name="First library", user=self.user1)
        clone = create_copy_of_instance(instance, attrs={"user": self.user2})

        self.assertNotEqual(instance.pk, clone.pk)
        self.assertEqual(clone.user, self.user2)

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
