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

    class Meta:
        verbose_name = 'Form'
        verbose_name_plural = 'Forms'


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
        verbose_name = 'FormCompanyShare'
        verbose_name_plural = 'FormCompanyShares'


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
        verbose_name = 'FormUserShare'
        verbose_name_plural = 'FormUserShares'


class DocumentRecipient(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    access_code = models.CharField(max_length=12, null=True)

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

class FormDocumentResponse(TimeStampedModel):
    """
    FormDocumentResponse represents Form submission per User
    When form is published, users registered to platform or anonymous users can submit form

    """
    receiver_user = models.ForeignKey(User, null=True, help_text='The user who submitted the form, optional')
    sender_user = models.ForeignKey(User, null=True, help_text='The user who submitted the form, optional')
    last_interactive_timestamp = models.DateTimeField(auto_now=True, auto_now_add=True)
    form_document = models.ForeignKey(FormDocument)
    form_response_data = JSONField()
    status = models.SmallIntegerField(choices=FORM_COMPLETION_STATUS, default=UNOPENED)

    class Meta:
        verbose_name = 'FormResponse'
        verbose_name_plural = 'FormResponses'


class FormDocumentResponseUserPermission(TimeStampedModel):
    from_user = models.ForeignKey(User)
    to_user = models.ForeignKey(User)
    response = models.ForeignKey(FormDocumentResponse)


class FormDocumentResponseCompanyPermission(TimeStampedModel):
    from_company = models.ForeignKey(Company)
    to_company = models.ForeignKey(Company)
    response = models.ForeignKey(FormDocumentResponse)


class FormDocumentLink(TimeStampedModel, DocumentRecipient):
    """
    Model to track document recipient whether or not opened
    the form or not
    """
    form_response = models.OneToOneField(FormDocumentResponse, null=True)
    from_user = models.ForeignKey(User)
    hash = models.CharField(max_length=128)
