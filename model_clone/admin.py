from django.contrib.admin import ModelAdmin
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.contrib.admin.options import TO_FIELD_VAR
from django.contrib.admin.utils import unquote
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from model_clone.mixin import CloneMixin


class CloneModelAdminMixin(object):
    """Mixin to handle duplication of models."""

    include_duplicate_action = True
    include_duplicate_object_link = True

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        extra_context["include_duplicate_object_link"] = (
            self.include_duplicate_object_link
        )
        if self.include_duplicate_object_link:
            to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
            if to_field and not self.to_field_allowed(request, to_field):
                raise DisallowedModelAdminToField(
                    "The field %s cannot be referenced." % to_field
                )

            obj = self.get_object(request, unquote(object_id), to_field)

            if obj is not None and request.GET.get("duplicate") == "true":
                clone = obj.make_clone()
                clone.save()
                self.message_user(
                    request,
                    _("Duplication successful, redirected to cloned: {}").format(clone),
                )
                cloned_admin_url = reverse(
                    "admin:{0}_{1}_change".format(
                        clone._meta.app_label, clone._meta.model_name
                    ),
                    args=(clone.pk,),
                )
                return HttpResponseRedirect(cloned_admin_url)

        return super().changeform_view(request, object_id, form_url, extra_context)

    def make_clone(self, request, queryset):
        clone_obj_ids = []

        for obj in queryset:
            clone = obj.make_clone()
            clone.save()
            clone_obj_ids.append(str(clone.pk))

        if clone_obj_ids:
            self.message_user(
                request,
                _("Successfully created: {} new duplicates").format(len(clone_obj_ids)),
            )

    make_clone.short_description = _("Duplicate selected %(verbose_name_plural)s")

    def _get_base_actions(self, **kwargs):
        """Return the list of actions, prior to any request-based filtering."""
        # Django 6 passes ``action_location`` here and to ``get_action``, which
        # returns None for an action not offered at that location.
        actions = list(super()._get_base_actions(**kwargs))
        # Add the make clone action
        if self.include_duplicate_action and issubclass(self.model, CloneMixin):
            action = self.get_action("make_clone", **kwargs)
            if action:
                actions.append(action)

        return actions


class CloneModelAdmin(CloneModelAdminMixin, ModelAdmin):
    """Clone model admin view."""
