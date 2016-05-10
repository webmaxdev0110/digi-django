from django.contrib import admin



class NonSuperUserReadonlyAdmin(admin.ModelAdmin):

    def __init__(self, model, admin_site):
        super(NonSuperUserReadonlyAdmin, self).__init__(model, admin_site)

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [field.name for field in filter(lambda f: not f.auto_created, self.model._meta.fields)]
        else:
            return super(NonSuperUserReadonlyAdmin, self).get_readonly_fields(request, obj)

    def get_actions(self, request):
        if not request.user.is_superuser:
            return []
        else:
            return super(NonSuperUserReadonlyAdmin, self).get_actions(request)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not request.user.is_superuser:
            extra_context = extra_context or {}
            extra_context['show_save'] = False
            extra_context['show_save_and_continue'] = False

        return super(NonSuperUserReadonlyAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context)

