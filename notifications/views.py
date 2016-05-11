from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging

# Get an instance of a logger
from notifications.models import SMSNotificationTransaction

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
    # Sample format
    # {
    #     "messageId": "E89196B793D930B4",
    #     "status": "READ",
    #     "acknowledgedTimestamp": "2014-10-26T23:10:00+11:00",
    #     "content": "Some response"
    # }
    message_id = request.POST.get('messageId')
    if message_id:
        qs = SMSNotificationTransaction.objects.filter(
            remote_id=message_id
        )
        if qs.exists():
            transaction = qs[0]
            transaction.user_response = request.POST.get('content')
            transaction.save()
    return HttpResponse('')