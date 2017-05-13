from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from core.constants import (
    STATUS_CHOICES,
    PublishStatus,
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


class PublishableModel(models.Model):
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PublishStatus.DRAFT)

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


class SelfAwareModel(models.Model):
    """Model that is aware of its own ContentType"""

    class Meta(object):
        abstract = True

    @classmethod
    def get_ct(cls):
        """Returns the ContentType for this model"""
        return ContentType.objects.get_for_model(cls)

    def get_ct_id(self):
        """Returns the ContentType.id for this model"""
        return self.get_ct().pk

    def get_app_label(self):
        return self.get_ct().app_label

    def get_model_name(self):
        return self.get_ct().model_name


class ArchiveMixin(models.Model):
    archived_on = models.DateTimeField(null=True)

    class Meta:
        abstract = True

    def archive(self):
        self.archived_on = now()
        self.save()
