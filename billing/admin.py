from django.contrib import admin
from django.contrib.admin import ModelAdmin

from billing.models import Plan


class PlanAdmin(ModelAdmin):
    list_display = (
        'name',
        'price_cents',
        'recurring_type',
        'is_live',
        'min_required_num_user',
        'max_num_user',
        'trial_days',
    )
    list_filter = ('is_live', 'recurring_type',)


admin.site.register(Plan, PlanAdmin)
