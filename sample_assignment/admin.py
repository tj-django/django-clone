from django.contrib import admin
from sample_assignment.models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    pass
