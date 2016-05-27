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


class FormDocumentUserShare(TimeStampedModel):
    """
    FormDocumentUserShare represents sharings of form(document) with individual users
    There're 2 cases for sharing of document.
        - share with company
        - share with individual users
    And this model represents second case.

    """
    form_document = models.ForeignKey(FormDocument, related_name="shares_to_users")
    shared_to_user = models.ForeignKey(User, related_name="shares_from_users")

    # if form is shared with company and "shared_to_user" is company member,
    # shared_by would link to company
    shared_by = models.ForeignKey(FormDocumentCompanyShare, null=True)

    # Send form response result automatically to FormDocument Owner
    send_response_to_owner_automatically = models.BooleanField(default=True,
        help_text="Send form response result to Form owner automatically")

    class Meta:
        unique_together = (('form_document', 'shared_to_user'),)


FROM_OWNER = 0
FROM_SHARED_USER = 1
FROM_SHARED_COMPANY = 2

AVAILABLE_FORM_SOURCES = (
    (FROM_OWNER, _('From form owner')),
    (FROM_SHARED_USER, _('From shared user')),
    (FROM_SHARED_COMPANY, _('From shared company')),
)


class FormDocumentSource(TimeStampedModel):
    """
    FormDocumentSource represents where form comes from

    If form comes from 'shared user', user_share field would be filled
    If form comes from 'shared company admin', company_share field would be filled
    If form comes from 'shared company user', company_share_user field would be filled
    """
    source = models.SmallIntegerField(default=FROM_OWNER, choices=AVAILABLE_FORM_SOURCES)
    user_share = models.ForeignKey(FormDocumentUserShare, null=True)
    company_share = models.ForeignKey(FormDocumentCompanyShare, null=True)


class RecipientTracking(models.Model):
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=30, null=True)

    class Meta:
        abstract = True


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

class FormDocumentResponse(TimeStampedModel, RecipientTracking):
    """
    FormDocumentResponse represents Form submission per User
    When form is published, users registered to platform or anonymose users can submit form
    """
    user = models.ForeignKey(User, null=True, help_text='The user who submitted the form, optional')
    form = models.ForeignKey(FormDocument)
    form_response_data = JSONField()
    status = models.SmallIntegerField(choices=FORM_COMPLETION_STATUS, default=UNOPENED)
    form_source = models.ForeignKey(FormDocumentSource)

