from django.contrib.admin import ModelAdmin
from django.contrib import admin
from identity_verification.models import PersonVerification


class PersonVerificationAdmin(ModelAdmin):
    list_display = [
        'get_person_first_name',
        'get_person_last_name',
        'country',
    ]
    list_filter = (
        'country',
    )

    def get_person_first_name(self, obj):
        return obj.person.first_name
    get_person_first_name.admin_order_field = 'person__first_name'
    get_person_first_name.short_description = 'First Name'

    def get_person_last_name(self, obj):
        return obj.person.last_name
    get_person_first_name.admin_order_field = 'person__last_name'
    get_person_first_name.short_description = 'Last Name'


admin.site.register(PersonVerification, PersonVerificationAdmin)

