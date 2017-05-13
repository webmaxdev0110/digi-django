from django.utils.translation import ugettext_lazy as _


class PublishStatus(object):
    DRAFT = 0
    LIVE = 1

STATUS_CHOICES = (
    (PublishStatus.DRAFT, _('Draft')),
    (PublishStatus.LIVE, _('Live')),
)