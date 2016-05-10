from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


@csrf_exempt
def plivo_sms_callback_handler(request):
    logger.info('plivo_sms_callback_handler', exe_info=True, extra={
        'request': request,
    })

@csrf_exempt
def plivo_sms_status_callback_handler(request):
    logger.info('plivo_sms_status_callback_handler', exe_info=True, extra={
        'request': request,
    })


@csrf_exempt
def telstra_sms_callback_handler(request):
    logger.info('telstra_sms_callback_handler', exe_info=True, extra={
        'request': request,
    })
    return HttpResponse('ok')