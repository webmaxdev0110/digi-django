import logging
import sys

from django.http import (
    HttpResponseServerError,
)
from django.template.context_processors import static
from django.views.debug import technical_500_response



def handler500(request):
    """
    An error handler which exposes the request object to the error template.
    """
    # Show admins a page with stacktrace
    if hasattr(request, 'user') and request.user.is_staff:
        return technical_500_response(request, *sys.exc_info())

    try:
        context = static(request)  # adds STATIC_URL
    except Exception as e:
        logging.error(e, exc_info=sys.exc_info(), extra={'request': request})
        context = {}

    try:
        context['exception_type'] = type(sys.exc_info()[1]).__name__
        context['exception'] = sys.exc_info()[1]
    except Exception:
        context['exception_type'] = 'Error'
        context['exception'] = 'Error getting exception'

    context['request'] = request

    return HttpResponseServerError('500 error')
