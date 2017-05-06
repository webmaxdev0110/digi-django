from emails.apis import (
    get_email_rendering_base_context,
    render_html_email,
    render_text_email,
)
from emondo.celery import app
from notifications.tasks import send_one_off_email


@app.task
def send_trackable_form_link_email(form_tracking_url, to_address):
    subject = 'You received a form completion request'
    context = get_email_rendering_base_context()
    context.update({
        'form_tracking_url': form_tracking_url
    })
    html_email = render_html_email('form_link_invitation', context)
    text_email = render_text_email('form_link_invitation', context)
    send_one_off_email.delay(subject, [to_address], text_email, html_email)
