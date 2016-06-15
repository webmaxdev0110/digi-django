from celery.task import task
from notifications.apis import (
    send_sms_message,
    send_email,
)
from emondo.celery import app



@app.task
def send_one_off_sms_message(number, text, provider='plivo'):
    send_sms_message(number, text, provider)


@app.task
def send_one_off_email(subject, to_address, text_email='', html_email='', tags=None, metadata=None):
    send_email(subject, to_address, text_email, html_email, tags, metadata)
