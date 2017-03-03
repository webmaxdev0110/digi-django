import stripe
from django.conf import settings


def create_stripe_card_token(cc_number, exp_month, exp_year, cvc):
    stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_customer(card_token, description=''):
    stripe.api_key = settings.STRIPE_API_KEY
    customer = stripe.Customer.create(
        description=description,
        source=card_token
    )
    return customer

    stripe.api_key = settings.STRIPE_API_KEY
    stripe.Charge.create(
      amount=99999999,
      currency="aud",
      customer='cus_96GD5UWPEo94pK',
      description="Charge for emondo business plan"
    )
def charge_stripe_customer(user, amount_cents, description):
    stripe.api_key = settings.STRIPE_API_KEY
    stripe_customer = None
    try:
        stripe_customer = user.stripecustomer
    except StripeCustomer.DoesNotExist:
        logger.error("Stripe customer does not exist", kwargs={
            'user_id': user.pk,
            'amount_cents': amount_cents,
            'description': description
        })
        return False

    charge = stripe.Charge.create(
        amount=amount_cents,
        currency="aud",
        customer=stripe_customer.customer_id,
        description=description,
        capture=True        # Charge immediately
    )
    if charge['piad'] == True:
        Transaction.create(user, amount_cents, description)
    else:
        raise CardChargeFailedException({
            "stripe_customer_id": stripe_customer.customer_id,
            "amount_cents": amount_cents,
            "description": description
        })

    return True


def subscribe_user_to_plan(user, plan_pricing, num_of_users):
    stripe.api_key = settings.STRIPE_API_KEY
    stripe_customer = None
    try:
        stripe_customer = user.stripecustomer
    except StripeCustomer.DoesNotExist:
        logger.error("Stripe customer does not exist", kwargs={
            'user_id': user.pk
        })
        return

    assert isinstance(plan_pricing, PlanPricing)
    pricing_amount = plan_pricing.pricing.price_cents * num_of_users
    trial_days = plan_pricing.trial_days
    subscription = PlanSubscription(
        user=user,
        active=True,
        number_of_users=num_of_users,
        next_payment_date=now().date() + timedelta(days=trial_days),
        plan_pricing=plan_pricing
    )

    if trial_days == 0:
        charge_strip_customer(user.stripecustomer, pricing_amount, "Subscribe for %s" % plan_pricing.plan.name)
        subscription.active = True
    else:
        subscription.active = True

    subscription.save()
    return subscription
