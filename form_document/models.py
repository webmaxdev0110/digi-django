from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.models import Site
from django.db import models

from accounts.models import User, Company
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


UNOPENED = 1
OPENED = 2
SAVED = 3
SUBMITTED = 4
ABANDONED = 5

FORM_COMPLETION_STATUS = (
    (UNOPENED, _('Unopen')),
    (ABANDONED, _('Abandoned')),
    (OPENED, _('Opened')),
    (SAVED, _('Saved')),
    (SUBMITTED, _('Submitted')),
)

class FormDocumentResponse(TimeStampedModel):
    """
    FormDocumentResponse represents Form submission per User
    When form is published, users registered to platform or anonymose users can submit form
    """
    user = models.ForeignKey(User, null=True, help_text='The user who submitted the form, optional')
    form = models.ForeignKey(FormDocument)
    form_response_data = JSONField()
    status = models.SmallIntegerField(choices=FORM_COMPLETION_STATUS, default=UNOPENED)


class FormDocumentUserShare(TimeStampedModel):
    """
    FormDocumentUserShare represents sharings of form(document) with individual users
    There're 2 cases for sharing of document.
        - share with company
        - share with individual users
    And this model represents second case.

    """
    form_document = models.ForeignKey(FormDocument, related_name="shares_to_users")
    user = models.ForeignKey(User, related_name="shares_from_users")

    # Send form response result automatically to FormDocument Owner
    send_response_to_owner_automatically = models.BooleanField(default=True,
        help_text="Send form response result to Form owner automatically")

    class Meta:
        unique_together = (('form_document', 'user'),)


class FormDocumentCompanyShare(TimeStampedModel):
    """
    FormDocumentCompanyShare represents first case of sharing document.

    """
    form_document = models.ForeignKey(FormDocument, related_name="shares_to_companies")
    company = models.ForeignKey(Company, related_name="shares_from_companies")

    # field to share a "shared form for organisation" to organisation members
    share_to_all_members = models.BooleanField(default=False)

    class Meta:
        unique_together = (('form_document', 'company'),)


class FormDocumentCompanyUserShare(TimeStampedModel):
    """
    If document is shared with company, 
        - company manager can decide to share it all with team members,
        - or share with specific team members
    FormDocumentCompanyShare.share_to_all_members is for 1st case
    And FormDocumentCompanyUserShare represents 2nd case
    """
    share_obj = models.ForeignKey(FormDocumentCompanyShare, related_name="shares_among_members")
    user = models.ForeignKey(User)

