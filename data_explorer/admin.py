from django.contrib import admin

# Register your models here.
from core.admin_mixins import NonSuperUserReadonlyAdmin
from data_explorer.models import (
    AFSLicenseeEntry,
    AFSAuthorisedRepresentative,
    JusticeOfPeace,
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


class JusticeOfPeaceAdmin(NonSuperUserReadonlyAdmin, admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'jp_number',
        'suburb',
        'state',
    ]
    list_filter = (
        'state',
        'suburb',
    )
    search_fields = (
        'first_name',
        'last_name',
        'jp_number',
        'suburb',
        'state',
        'mobile_phone',
        'phone',
    )


admin.site.register(AFSLicenseeEntry, AFSLicenseeEntryAdmin)
admin.site.register(AFSAuthorisedRepresentative, AFSAuthorisedRepresentativeAdmin)
admin.site.register(JusticeOfPeace, JusticeOfPeaceAdmin)
