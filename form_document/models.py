from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.models import Site
from django.db import models
from accounts.models import User
from core.models import TimeStampedModel


class FormDocument(TimeStampedModel):
    """
    Represents a form document created by an user
    The form should be accessible by document owner,
    owner's organisation account admin
    """

    slug = models.SlugField(
        unique=True, null=True,
        help_text='Use for short URL sharing')
    title = models.CharField(max_length=256, default='Untitled Form')
    uploaded_document = models.FileField(
        null=True, help_text='The document uploaded used for populating after a form is completed')
    user = models.ForeignKey(User, help_text='The owner of this document')
    form_data = JSONField()      # All the form data
    site = models.ForeignKey(Site)

    def __unicode__(self):
        return '<FormDocument: {0}>'.format(self.title[:16])


ABANDONED = 0
OPENED = 1
SAVED = 2
COMPLETED = 3

FORM_COMPLETION_STATUS = (
    (ABANDONED, _('abandoned')),
    (OPENED, _('opened')),
    (SAVED, _('saved')),
    (COMPLETED, _('completed')),
)


class FormDocumentResponse(TimeStampedModel):
    user = models.ForeignKey(
        User,
        null=True,
        help_text='The user who submitted the form, optional')
    form = models.ForeignKey(FormDocument)
    form_response_data = JSONField()
    status = models.CharField(max_length=100, choices=FORM_COMPLETION_STATUS)
    
