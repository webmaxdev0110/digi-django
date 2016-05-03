from django.contrib import admin

# Register your models here.
from core.admin_mixins import NonSuperUserReadonlyAdmin
from data_explorer.models import (
    AFSLicenseeEntry,
    AFSAuthorisedRepresentative,
)


class AFSLicenseeEntryAdmin(NonSuperUserReadonlyAdmin, admin.ModelAdmin):
    list_display = [
        'name',
        'license_no',
        'abn',
        'commenced_date',
        'status'
    ]
    list_filter = (
        'status',
    )
    search_fields = (
        'name',
        'license_no',
        'abn',
    )
    date_hierarchy = 'commenced_date'


class AFSAuthorisedRepresentativeAdmin(NonSuperUserReadonlyAdmin, admin.ModelAdmin):
    list_display = [
        'name',
        'license_no',
        'licensed_by'
    ]
    list_filter = (
        'licensed_by',
    )
    search_fields = (
        'name',
        'license_no',
        'licensed_by__name',
    )


admin.site.register(AFSLicenseeEntry, AFSLicenseeEntryAdmin)
admin.site.register(AFSAuthorisedRepresentative, AFSAuthorisedRepresentativeAdmin)
