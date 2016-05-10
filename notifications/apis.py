from notifications.vendors.plivo_sms import (
    send_plivo_sms,
)
from notifications.vendors.telstra_sms import send_telstra_sms
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def send_sms_message(number, text, provider='plivo'):
    if provider == 'plivo':
        send_plivo_sms(number, text)
    elif provider == 'telstra':
        send_telstra_sms(number, text)
    else:
        logger.warning('Unkown SMS provider {0}'.format(provider))