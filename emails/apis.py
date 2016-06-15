from django.template.loader import get_template
from premailer import transform


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
    t = get_template(email_template_path)
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
