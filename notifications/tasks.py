from celery.task import task
from notifications.apis import send_sms_message

@task
def send_one_off_sms_message(number, text, provider='plivo'):
    send_sms_message(number, text, provider)