from django.utils.translation import ugettext_lazy as _


class StatusChoices(object):
    DRAFT = 0
    LIVE = 1

STATUS_CHOICES = (
    (StatusChoices.DRAFT, _('Draft')),
    (StatusChoices.LIVE, _('Live')),
)