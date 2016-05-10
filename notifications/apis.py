from notifications.models import SMSNotificationTransaction
from notifications.vendors.plivo_sms import (
    send_plivo_sms,
)
from notifications.vendors.telstra_sms import send_telstra_sms
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
            remote_id=json.loads(result['text'])['messageId']
        )
    else:
        logger.warning('Unkown SMS provider {0}'.format(provider))