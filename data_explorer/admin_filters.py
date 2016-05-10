from django.contrib.admin import SimpleListFilter

# admin.py
class HasMobileNumberFilter(SimpleListFilter):
    title = 'has mobile' # or use _('country') for translated title
    parameter_name = 'mobile_number'

    def lookups(self, request, model_admin):
        return [
            (1, 'Yes',),
            (0, 'No',),
        ]


    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(mobile_number='')
        else:
            return queryset

#