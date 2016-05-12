from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from accounts.models import User

class EmondoUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('date_joined', 'signup_tag_index', 'signup_form_source',)

    def get_fieldsets(self, request, obj=None):
        fieldset = super(EmondoUserAdmin, self).get_fieldsets(request, obj)

        fieldset += (
            ('Others', {
                'fields': ('avatar', 'short_description',),
            }),
        )
        return fieldset




admin.site.register(User, EmondoUserAdmin)

