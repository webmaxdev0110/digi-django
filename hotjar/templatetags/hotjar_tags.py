from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(
    'hotjar/elements/hotjar_tracking_integration.html')
def include_hotjar():
    return {
        'include_hotjar': not settings.DEBUG,
    }
