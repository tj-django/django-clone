from unittest import skipUnless

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from model_clone import CloneModelAdmin
from sample.models import Book

ActionLocation = getattr(admin, "ActionLocation", None)


class CloneModelAdminActionsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser(
            username="admin", email="admin@example.com", password=None
        )

    def setUp(self):
        self.request = RequestFactory().get("/admin/sample/book/")
        self.request.user = self.user

    def test_get_actions_includes_make_clone(self):
        model_admin = CloneModelAdmin(Book, AdminSite())

        actions = model_admin.get_actions(self.request)

        self.assertIn("make_clone", actions)

    @skipUnless(ActionLocation, "action locations were added in Django 6")
    def test_make_clone_is_not_a_change_form_action(self):
        model_admin = CloneModelAdmin(Book, AdminSite())

        actions = model_admin.get_actions(
            self.request, action_location=ActionLocation.CHANGE_FORM
        )

        self.assertNotIn("make_clone", actions)

    def test_get_actions_omits_make_clone_when_disabled(self):
        model_admin = CloneModelAdmin(Book, AdminSite())
        model_admin.include_duplicate_action = False

        actions = model_admin.get_actions(self.request)

        self.assertNotIn("make_clone", actions)
