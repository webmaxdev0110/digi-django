
import requests
import json
from django.conf import settings


def send_telstra_sms(number, message):

    APP_KEY = settings.TELSTRA_SMS_APPKEY  # Get from https://dev.telstra.com/user/me/apps
    APP_SECRET = settings.TELSTRA_SMS_APPSECRET  # Get from https://dev.telstra.com/user/me/apps

    tokenPayload = {
        'client_id': APP_KEY,
        'client_secret': APP_SECRET,
        'grant_type' : 'client_credentials',
        'scope' : 'SMS'
    }

    request = "https://api.telstra.com/v1/oauth/token"
    response = json.loads(requests.get(request, params=tokenPayload).text)
    TOKEN = response['access_token']

    payload = {
        'to': number,
        'body': message
    }

    r = requests.post('https://api.telstra.com/v1/sms/messages',
                      headers = {'Content-Type' : 'application/json',
                                 'Authorization' : 'Bearer ' + TOKEN},
                      data = json.dumps(payload))

    return {
        'status': r.status_code,
        'text': r.text
    }