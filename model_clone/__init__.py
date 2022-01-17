"""Top-level package for django-clone."""

__author__ = """Tonye Jack"""
__email__ = "jtonye@ymail.com"
__version__ = "3.0.1"

from model_clone.admin import CloneModelAdmin, CloneModelAdminMixin
from model_clone.mixin import CloneMixin
from model_clone.utils import create_copy_of_instance

__all__ = [
    "CloneMixin",
    "CloneModelAdmin",
    "CloneModelAdminMixin",
    "create_copy_of_instance",
]
