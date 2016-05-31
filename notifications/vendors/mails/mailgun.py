from __future__ import unicode_literals
import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
import logging

logger = logging.getLogger(__file__)

DOMAIN = 'msg.emondo.com.au'
BASE_URL = 'https://api.mailgun.net/v3'


class Mailgun(object):
    def __init__(self, api_key=None):
        self.auth = ('api', api_key or settings.MAILGUN_PRIVATE_API_KEY)
        self.base_url = '{0}/{1}'.format(BASE_URL, DOMAIN)

    def post(self, path, data, files=None, include_domain=True):
        url = self.base_url if include_domain else BASE_URL
        return requests.post(url + path, auth=self.auth, data=data, files=files)

    def get(self, path, data, files=None, include_domain=False):
        url = self.base_url if include_domain else BASE_URL
        return requests.get(url + path, auth=HTTPBasicAuth(
            'api', settings.MAILGUN_PUBLIC_API_KEY), data=data, files=files)

    def validate_email(self, email):
        result = self.get('/address/validate', data={
            'address': email
        })
        result_json = {}
        try:
            result_json = result.json()
        except StandardError as e:
            logger.error(str(e), text_result=result.text)

        result = result_json.get('is_valid', False)

        return result
