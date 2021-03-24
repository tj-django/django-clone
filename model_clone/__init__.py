"""
Duplicate instances of a model using the following mixin and admin view.
"""

from model_clone.admin import CloneModelAdmin, CloneModelAdminMixin
from model_clone.mixins.clone import CloneMixin

__all__ = ["CloneMixin", "CloneModelAdmin", "CloneModelAdminMixin"]
