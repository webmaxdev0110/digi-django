from django.template.loader import get_template
from premailer import transform
from notifications.tasks import send_one_off_email


def render_html_email(template_name, context=None):
    """
    Render a html email using template
    :param template_name: The template folder name, not the full template path
    eg. templates/emails/verify_email_address/html_content.html
    only needs "verify_email_address" as template_name
    :param context: The render context for the html email
    """
    email_template_path = 'emails/{0}/html_content.html'.format(template_name)
    context = context or {}
    t = get_template(template_name)
    # todo: baseurl?
    return transform(t.render(context))

def render_text_email(template_name, context=None):
    """
    Render a text email using template
    :param template_name: The template folder name, not the full template path
    eg. templates/emails/verify_email_address/text_content.txt
    only needs "verify_email_address" as template_name
    :param context: The render context for the html email
    """
    email_template_path = 'emails/{0}/text_content.txt'.format(template_name)
    context = context or {}
    t = get_template(email_template_path)
    return t.render(context)


def send_account_email_verification_email(
        to_address,
        account_type, first_name, account_email_verification_link):
    subject = 'Complete your {0} emondo account'.format(account_type)
    context = {
        'subject': subject,
        'first_name': first_name,
        'email_verification_link': account_email_verification_link
    }
    html_email = render_html_email('verify_email_address', context)
    text_email = render_text_email('verify_email_address', context)
    send_one_off_email.delay(subject, [to_address], text_email, html_email)
