from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(
    'intercom/elements/intercom_integration.html')
def include_intercom():
    return {
        'include_intercom': not settings.DEBUG,
    }
