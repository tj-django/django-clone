from django.contrib.admin import ModelAdmin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


class ClonableModelAdmin(ModelAdmin):
    """Admin to handle duplication of models."""
    change_form_template = 'clone/change_form.html'

    def response_change(self, request, obj):
        if "_duplicate" in request.POST:
            clone = obj.make_clone()
            clone.save()
            self.message_user(
                request,
                _("Duplication successful, redirected to cloned admin")
            )
            cloned_admin_url = reverse(
                'admin:{0}_{1}_change'.format(
                    clone._meta.app_label,
                    clone._meta.model_name),
                    args=(clone.pk,)
            )
            return HttpResponseRedirect(cloned_admin_url)
        return super().response_change(request, obj)
