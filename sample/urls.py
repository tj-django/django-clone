from django.contrib import admin
from django.views.generic import RedirectView

try:
    from django.urls import re_path as path
except ImportError:
    from django.conf.urls import url as path

app_name = "sample"

urlpatterns = [
    path("^admin/", admin.site.urls, name='admin'),
    path("", RedirectView.as_view(pattern_name='admin:index')),
]
