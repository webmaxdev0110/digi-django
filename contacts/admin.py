from django.contrib.admin import ModelAdmin
from django.contrib import admin

from contacts.models import Person


class PersonAdmin(ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'middle_name',
        'email',
        'date_of_birth',
        'email',
        'gender',
        'mobile_number',
    )



admin.site.register(Person, PersonAdmin)

