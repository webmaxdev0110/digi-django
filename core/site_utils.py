from django.contrib.sites.models import Site
from django.http.request import split_domain_port

try:
    # python 2
    from urlparse import urlparse
except ImportError:
    # Python 3
    from urllib.parse import urlparse


def get_site_from_request_origin(request):
    origin = request.META.get('HTTP_ORIGIN', None)
    if not origin:
        return None

    netloc = urlparse(origin).netloc
    domain, port = split_domain_port(netloc)
    try:
        return Site.objects.get(domain=domain)
    except Site.DoesNotExist:
        return None

