from django.http import HttpResponsePermanentRedirect
from django.conf import settings


class HostnameRedirectMiddleware(object):
    def process_request(self, request):
        if not settings.DEBUG:
            if not request.META['HTTP_HOST'].endswith('emondo.com.au'):
                return HttpResponsePermanentRedirect('http://emondo.com.au/')
