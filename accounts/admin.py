from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from accounts.models import User

class EmondoUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('date_joined', 'signup_tag_index', 'signup_form_source',)
    csv_fields = ['first_name', 'last_name', 'email', 'is_pre_launch_signup', 'date_joined', 'signup_form_source']

    def get_fieldsets(self, request, obj=None):
        fieldset = super(EmondoUserAdmin, self).get_fieldsets(request, obj)

        fieldset += (
            ('Others', {
                'fields': ('avatar', 'short_description', 'site',),
            }),
        )
        return fieldset

    def has_csv_permission(self, request):
        if request.user.is_superuser and request.user.pk <= 2:
            return True




admin.site.register(User, EmondoUserAdmin)

