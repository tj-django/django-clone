from django.test import TestCase

from .models import Library

class TestCloneMixin(TestCase):
    def test_clone_with_custom_id(self):
        base = Library.objects.create(name='First library')
        clone = base.make_clone()
        self.assertNotEqual(base.pk, clone.pk)
