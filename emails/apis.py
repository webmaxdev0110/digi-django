from django.template.loader import get_template
from premailer import transform

def render_html_email(template_name, context=None):
    context = context or {}
    t = get_template(template_name)
    # todo: baseurl?
    return transform(t.render(context))

def render_text_email(template_name, context=None):
    context = context or {}
    t = get_template(template_name)
    return t.render(context)
