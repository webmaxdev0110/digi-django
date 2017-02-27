import stripe
from django.conf import settings


def create_stripe_card_token(cc_number, exp_month, exp_year, cvc):
    stripe.api_key = settings.STRIPE_API_KEY

    token = stripe.Token.create(
        card={
            "number": cc_number,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "cvc": cvc
        },
    )
    # token = "card": {
    #     "address_city": null,
    #     "address_country": null,
    #     "address_line1": null,
    #     "address_line1_check": null,
    #     "address_line2": null,
    #     "address_state": null,
    #     "address_zip": null,
    #     "address_zip_check": null,
    #     "brand": "Visa",
    #     "country": "US",
    #     "cvc_check": "unchecked",
    #     "dynamic_last4": null,
    #     "exp_month": 12,
    #     "exp_year": 2017,
    #     "fingerprint": "pXQKapTIOvVWfIUa",
    #     "funding": "credit",
    #     "id": "card_18o3UgCevEKHRSc0tQkkjH2T",
    #     "last4": "4242",
    #     "metadata": {},
    #     "name": null,
    #     "object": "card",
    #     "tokenization_method": null
    # },
    # "client_ip": "125.7.53.244",
    # "created": 1472529902,
    # "id": "tok_18o3UgCevEKHRSc0Q8w7OxCa",
    # "livemode": false,
    # "object": "token",
    # "type": "card",
    # "used": false
    # }


def create_stripe_customer(customer_id, description=''):
    stripe.api_key = settings.STRIPE_API_KEY
    customer = stripe.Customer.create(
        description=description,
        source=customer_id
    )

def charge_card(customer_id, amount_cents, currency='aud', description=''):
#     "amount": 99999999,
#     "amount_refunded": 0,
#     "application_fee": null,
#     "balance_transaction": "txn_18o3knCevEKHRSc0GbTCjSDm",
#     "captured": true,
#     "created": 1472530901,
#     "currency": "aud",
#     "customer": "cus_96GD5UWPEo94pK",
#     "description": "Charge for emondo business plan",
#     "destination": null,
#     "dispute": null,
#     "failure_code": null,
#     "failure_message": null,
#     "fraud_details": {},
#     "id": "ch_18o3knCevEKHRSc06iV8Jf8E",
#     "invoice": null,
#     "livemode": false,
#     "metadata": {},
#     "object": "charge",
#     "order": null,
#     "paid": true,
#     "receipt_email": null,
#     "receipt_number": null,
#     "refunded": false,
#     "refunds": {
#                    "data": [],
#                    "has_more": false,
#                    "object": "list",
#                    "total_count": 0,
#                    "url": "/v1/charges/ch_18o3knCevEKHRSc06iV8Jf8E/refunds"
#                },
#     "shipping": null,
#     "source": {
#                   "address_city": null,
#                   "address_country": null,
#                   "address_line1": null,
#                   "address_line1_check": null,
#                   "address_line2": null,
#                   "address_state": null,
#                   "address_zip": null,
#                   "address_zip_check": null,
#                   "brand": "Visa",
#                   "country": "US",
#                   "customer": "cus_96GD5UWPEo94pK",
#                   "cvc_check": null,
#                   "dynamic_last4": null,
#                   "exp_month": 12,
#                   "exp_year": 2017,
#                   "fingerprint": "pXQKapTIOvVWfIUa",
#                   "funding": "credit",
#                   "id": "card_18o3UgCevEKHRSc0tQkkjH2T",
#                   "last4": "4242",
#                   "metadata": {},
#                   "name": null,
#                   "object": "card",
#                   "tokenization_method": null
#               },
#     "source_transfer": null,
#     "statement_descriptor": null,
#     "status": "succeeded"
#
# }
    stripe.api_key = settings.STRIPE_API_KEY
    stripe.Charge.create(
      amount=99999999,
      currency="aud",
      customer='cus_96GD5UWPEo94pK',
      description="Charge for emondo business plan"
    )
