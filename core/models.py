from __future__ import unicode_literals


from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.constants import (
    STATUS_CHOICES,
    StatusChoices,
)


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        abstract = True


class StatusModel(models.Model):
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=StatusChoices.DRAFT)

    class Meta:
        abstract = True



class YesNoStatusChoice(object):
    UNKNOWN = 0
    PASSED = 1
    REJECTED = 2


YES_NO_CHOICES = (
    (YesNoStatusChoice.PASSED, _('Pass')),
    (YesNoStatusChoice.REJECTED, _('Rejected')),
    (YesNoStatusChoice.UNKNOWN, _('Unknown')),
)

class YesNoStatusField(models.Model):
    status = models.PositiveSmallIntegerField(choices=YES_NO_CHOICES, default=YesNoStatusChoice.UNKNOWN)

    class Meta:
        abstract = True
