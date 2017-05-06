from emails.apis import (
    get_email_rendering_base_context,
    render_html_email,
    render_text_email,
)
from emondo.celery import app
from notifications.tasks import send_one_off_email


@app.task
def send_trackable_form_link_email(form_tracking_url, to_address, form_title, company_name='', first_name=None):
    subject = 'My online form has arrived from %s' % company_name
    context = get_email_rendering_base_context()
    context.update({
        'form_tracking_url': form_tracking_url,
        'subject': subject,
        'form_title': form_title,
        'first_name': first_name,
        'company_name': company_name
    })
    html_email = render_html_email('form_link_invitation', context)
    text_email = render_text_email('form_link_invitation', context)
    send_one_off_email.delay(subject, [to_address], text_email, html_email)
