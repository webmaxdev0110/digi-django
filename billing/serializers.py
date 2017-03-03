from datetime import timedelta
from django.contrib.sites.models import Site
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from accounts.models import User
from billing.apis import create_stripe_customer, subscribe_user_to_plan
from billing.models import Plan, PlanSubscription, StripeCustomer, StripeCard, PlanPricing


class PlanSerializer(serializers.ModelSerializer):
    """
    This serializer is for return the plan details
    """
    currency = serializers.SerializerMethodField()
    purchase_options = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = (
            'name',
            'min_required_num_user',
            'purchase_options',
            'max_num_user',
            'currency',
        )

    def get_currency(self, instance):
        return 'AUD'

    def get_purchase_options(self, instance):
        return instance.get_purchase_options()



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
            'plan_pricing_id',
            'number_of_users',
            'client_ip',
            'stripe_card_id',
            'stripe_card_fingerprint',
            'stripe_card_token',
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
            raise serializers.ValidationError('Plan is not available for new purchase')
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
        # todo: Handle duplicated new subscription
        user, created = User.objects.get_or_create(email=kwargs['email'])
        stripe_customer = create_stripe_customer(kwargs['stripe_card_token'])
        django_customer, _ = StripeCustomer.objects.get_or_create(user=user)
        django_customer.customer_id = stripe_customer['id']
        django_customer.save()
        card = StripeCard.objects.create(
            customer=stripe_customer,
            card_id=kwargs['stripe_card_id'],
            token_id=kwargs['stripe_card_token'],
            fingerprint=kwargs['stripe_card_fingerprint'],
            card_brand=kwargs['card_brand'],
            card_country=kwargs['card_country'],
            card_last4=kwargs['card_last4'],
        )
        plan_pricing = PlanPricing.objects.get(pk=kwargs['plan_pricing_id'])

        inst = subscribe_user_to_plan(user, plan_pricing, kwargs['number_of_users'])
        return inst
