from emails.apis import (
    render_html_email,
    render_text_email,
    get_email_rendering_base_context,
)
from notifications.tasks import send_one_off_email


def send_email_verification_code(email, code):
    subject = 'Your email verification code to complete signing'
    context = get_email_rendering_base_context()
    context.update({'code': code})
    html_email = render_html_email('email_signing_verification_code', context)
    text_email = render_text_email('email_signing_verification_code', context)
    send_one_off_email.delay(subject, [email], text_email, html_email)
