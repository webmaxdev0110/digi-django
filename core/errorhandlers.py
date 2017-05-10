import logging
import sys

from django.http import (
    HttpResponseServerError,
)
from django.template import loader
from django.views.debug import technical_500_response



def handler500(request):
    """
    An error handler which exposes the request object to the error template.
    """
    # Show admins a page with stacktrace
    if hasattr(request, 'user') and request.user.is_staff:
        return technical_500_response(request, *sys.exc_info())

    template = loader.get_template('core/500.html')
    return HttpResponseServerError(template.render())

