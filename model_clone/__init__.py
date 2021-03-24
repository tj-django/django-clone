"""
Duplicate instances of a model using the following mixin and admin view.
"""

from model_clone.admin import CloneModelAdmin, CloneModelAdminMixin
from model_clone.mixins.clone import CloneMixin
from model_clone.utils import create_copy_of_instance

__all__ = [
    "CloneMixin",
    "CloneModelAdmin",
    "CloneModelAdminMixin",
    "create_copy_of_instance",
]
