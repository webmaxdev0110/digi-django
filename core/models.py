from __future__ import unicode_literals


from django.db import models
from django.utils.translation import ugettext_lazy as _


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


PENDING = 0
ADMIN_LIVE = 1
LIVE = 2

STATUS_CHOICES = (
    (PENDING, _('Pending')),
    (ADMIN_LIVE, _('Admin Visible')),
    (LIVE, _('Live')),
)

class StatusModel(models.Model):
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    class Meta:
        abstract = True


UNKNOWN = 0
PASSED = 1
REJECTED = 2


YES_NO_CHOICES = (
    (PASSED, _('Pass')),
    (REJECTED, _('Rejected')),
    (UNKNOWN, _('Unknown')),
)

class YesNoStatusField(models.Model):
    status = models.PositiveSmallIntegerField(choices=YES_NO_CHOICES)

    class Meta:
        abstract = True
