

from notifications.models import SMSNotificationTransaction
from notifications.vendors.plivo_sms import (
    send_plivo_sms,
)
from notifications.vendors.telstra_sms import send_telstra_sms
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


def send_sms_message(number, text, provider='plivo'):
    if provider == 'plivo':
        result = send_plivo_sms(number, text)
        SMSNotificationTransaction.objects.create(
            remote_id=result['message_id']
        )

    elif provider == 'telstra':
        result = send_telstra_sms(number, text)
        SMSNotificationTransaction.objects.create(
            remote_id=json.loads(result['text'])['messageId'],
            dest_number=number
        )
    else:
        logger.warning('Unkown SMS provider {0}'.format(provider))



def send_email(subject, to_address, text_email='', html_email='', tags=None, metadata=None):
    # to=["New User <user1@example.com>", "account.manager@example.com"]
    from_email = "emondo <{0}>".format(settings.DEFAULT_FROM_EMAIL)
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_email,
        from_email=from_email,
        to=to_address,
        reply_to=[from_email])

    msg.attach_alternative(html_email, "text/html")

    # Optional Anymail extensions:
    msg.metadata = metadata
    msg.tags = tags
    msg.track_clicks = True

    # Send it:
    msg.send()



