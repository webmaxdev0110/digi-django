from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(
    'google_analytics/elements/google_analytics_integration.html')
def include_google_analytics():
    return {
        'include_ga': not settings.DEBUG,
    }



@register.inclusion_tag(
    'google_analytics/elements/mixpanel.html')
def include_mixpanel():
    return {
        'include_mixpanel': not settings.DEBUG,
    }
