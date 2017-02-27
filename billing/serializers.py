from django.contrib.sites.models import Site
from rest_framework import serializers
from rest_framework.serializers import Serializer, ModelSerializer

from billing.models import Plan, PlanSubscription


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


class SubscriptionSerializer(ModelSerializer):

    email = serializers.CharField(max_length=64)
    subdomain = serializers.CharField(max_length=64)
    plan_name = serializers.CharField(max_length=64)
    number_of_users = serializers.IntegerField()
    billing_cycle = serializers.CharField(max_length=64)
    client_ip = serializers.CharField(max_length=16)
    stripe_card_id = serializers.CharField(max_length=30)
    card_brand = serializers.CharField(max_length=16)
    card_country = serializers.CharField(max_length=16)
    card_last4 = serializers.CharField(max_length=4)

    class Meta:
        model = PlanSubscription
        fields = (
            'email',
            'subdomain',
            'plan_name',
            'number_of_users',
            'billing_cycle',
            'client_ip',
            'stripe_card_id',
            'card_brand',
            'card_country',
            'card_last4',
        )


    def validate_subdomain(self, value):
        if Site.objects.filter(domain=value).exists:
            raise serializers.ValidationError('Subdomain name already exists')
        return value

    def validate_plan_name(self, value):
        if not Plan.objects.filter(name=value, is_live=True).exists():
            raise serializers.ValidationError('Plan is not available for purchase')
        return value

    def validate_number_of_users(self, value):
        plan_name = self.initial_data['plan_name']
        plans = Plan.objects.filter(name=plan_name)
        # todo: filter live plan
        if plans.exists() and plans[0].is_num_user_valid(value):
            return value
        else:
            raise serializers.ValidationError('Number of user is invalid')



    def save(self, **kwargs):
        # 1. Create token
        # 2. Create customer
        # 3. Create subscription
        # 4. Create transaction (and Charge the card)
        # 4.
        # todo: to be implemented
        pass
