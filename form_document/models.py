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

    title = models.CharField(max_length=256, default='Untitled Form')
    slug = models.SlugField(null=True, help_text='Use for short URL sharing')

    uploaded_document = models.FileField(
        null=True, 
        help_text='The document uploaded used for populating after a form is completed')
    form_data = JSONField()      # All the form data

    owner = models.ForeignKey(User, help_text='The owner of this document')
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
    status = models.CharField(max_length=2, choices=FORM_COMPLETION_STATUS)
    

CAN_READ = 0
CAN_UPDATE = 1

FORM_DOCUMENT_PERMISSIONS = (
    (CAN_READ, _('Can read form_document')),
    (CAN_UPDATE, _('Can update form_document')),
)

class FormDocumentUserShare(models.Model):
    """
    FormDocumentUserShare represents sharings of form(document) with individual users
    There're 2 cases for sharing of document.
        - share with company
        - share with individual users (within company or user outside company)
    And this model represents second case.

    Regarding document's permission, we don't have "delete" permission for shared users.
    Only document owner can delete his own document.
    """
    form_document = models.ForeignKey(FormDocument, related_name="shares")
    user = models.ForeignKey(User, related_name="shared_documents")
    permission = models.SmallIntegerField(choices=FORM_DOCUMENT_PERMISSIONS, default=CAN_READ)


class FormDocumentCompanyShare(models.Model):
    """
    FormDocumentCompanyShare represents first case of sharing document.
    Relation between this model and FormDocument is OneToOneField.
    """
    form_document = models.OneToOneField(FormDocument, related_name="share_in_company")
    permission = models.SmallIntegerField(choices=FORM_DOCUMENT_PERMISSIONS, default=CAN_READ)

