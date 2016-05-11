from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging
import json

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

    body_unicode = request.body.decode('utf-8')
    body_data = json.loads(body_unicode)

    message_id = body_data.get('messageId')
    if message_id:
        qs = SMSNotificationTransaction.objects.filter(
            remote_id=message_id
        )
        if qs.exists():
            transaction = qs[0]
            transaction.user_response = body_data.get('content')
            transaction.status = body_data.get('status')
            transaction.save()
    return HttpResponse('')