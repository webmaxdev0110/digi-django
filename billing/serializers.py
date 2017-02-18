from rest_framework import serializers

from billing.models import Plan


class PlanSerializer(serializers.ModelSerializer):
    """
    This serializer is for return the plan details
    """
    currency = serializers.SerializerMethodField()
    recurring_type = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = (
            'name',
            'price_cents',
            'recurring_type',
            'min_required_num_user',
            'max_num_user',
            'trial_days',
            'currency',
        )

    def get_currency(self, instance):
        return 'AUD'

    def get_recurring_type(self, instance):
        return instance.get_recurring_type_display()
