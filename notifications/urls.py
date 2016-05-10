
from django.conf.urls import url

from notifications.views import (
    plivo_sms_callback_handler,
    plivo_sms_status_callback_handler,
)

urlpatterns = [

    url(r'^sms_callback/plivo/$', plivo_sms_callback_handler, name='plivo_sms_callback'),
    url(r'^sms_callback/plivo/status_report$', plivo_sms_status_callback_handler, name='plivo_sms_status_callback'),
]