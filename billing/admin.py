from django.contrib import admin
from django.contrib.admin import ModelAdmin

from billing.models import Plan, Pricing, PlanPricing, PlanSubscription


class PlanAdmin(ModelAdmin):
    list_display = (
        'name',
        'is_live',
        'min_required_num_user',
        'max_num_user',
    )
    list_filter = ('is_live',)
    readonly_fields = ('feature_flags',)


class PricingAdmin(ModelAdmin):
    list_display = (
        'name',
        'recurring_type',
    )
    list_filter = ('recurring_type',)


class PlanPricingAdmin(ModelAdmin):
    list_display = (
        'plan',
        'pricing',
        'trial_days',
    )


class PlanSubscriptionAdmin(ModelAdmin):
    list_display = (
        'user',
        'amount_cents',
        'start_date',
        'active',
        'user_cancelled',
        'system_cancelled',
        'next_payment_date',
    )

    readonly_fields = (
        'user', 'amount_cents', 'start_date',
    )

    list_filter = ('active', 'user_cancelled', 'system_cancelled',)

class TransactionAdmin(ModelAdmin):
    list_display = (
        'user',
        'amount_cents',
    )

    readonly_fields = (
        'user', 'reason', 'description', 'amount_cents',
    )


admin.site.register(Plan, PlanAdmin)
admin.site.register(Pricing, PricingAdmin)
admin.site.register(PlanPricing, PlanPricingAdmin)
admin.site.register(PlanSubscription, PlanSubscriptionAdmin)
