import plivo
from django.conf import settings


def send_plivo_sms(number, message):
    PLIVO_AUTH_ID = settings.PLIVO_AUTH_ID
    PLIVO_TOKEN = settings.PLIVO_TOKEN
    if not PLIVO_AUTH_ID or not PLIVO_TOKEN:
        raise Exception('PLIVO_AUTH_ID or PLIVO_TOKEN not configured')

    p = plivo.RestAPI(PLIVO_AUTH_ID, PLIVO_TOKEN)

    params = {
        'src': 'emondo', # Sender's phone number with country code
        'dst' : number,
        'text' : message,
        'url' : "https://emondo.com.au/notification/sms_callback/plivo/status_report/",
        'method' : 'POST'
    }

    response = p.send_message(params)
    return {
        'status': response[0],
        'message_id': response[1]['message_uuid']
    }

