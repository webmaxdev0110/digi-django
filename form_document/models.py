from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import (
    JSONField,
    ArrayField,
)
from django.contrib.sites.models import Site
from django.db import models
from storages.backends.gs import GSBotoStorage

from accounts.models import User, Company
from core.models import TimeStampedModel
import os


def document_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    file_name_no_extension = os.path.splitext(filename)
    return 'documents/users/{0}/{1}/{2}'.format(
        instance.owner.pk,
        file_name_no_extension,
        filename
    )

ProtectedStorage = lambda bucket: GSBotoStorage(
    acl='private',    # https://cloud.google.com/storage/docs/access-control/lists#predefined-acl
    bucket=bucket,
    querystring_auth=True,
    querystring_expire=600,
)
documents_store = ProtectedStorage('emondo-documents')

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
        upload_to=document_path,
        storage=documents_store,
        help_text='The document uploaded used for populating after a form is completed')
    processed_documents = ArrayField(
        models.FileField(upload_to=document_path),
        help_text='List of images that can be viewed in browser',
        storage=documents_store
    )
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
    FormDocumentCompanyShare represents a document to be shared
    within the user's company or to another company

    """
    form_document = models.ForeignKey(FormDocument, related_name="shares_to_companies")
    from_company = models.ForeignKey(Company, related_name="shares_from_companies")
    to_company = models.ForeignKey(Company)
    company_visible = models.BooleanField(
        default=False,
        help_text='If company visible is not true, only the compnay admin can view the document')

    class Meta:
        unique_together = (('form_document', 'company'),)
        verbose_name = 'FormCompanyShare'
        verbose_name_plural = 'FormCompanyShares'


class FormDocumentUserShare(TimeStampedModel):
    """
    FormDocumentUserShare represents sharings of form(document) with individual users (must be within the same company)
    There're 2 cases for sharing of document.
        - share with the entire company
        - share with individual company user
    And this model represents second case.

    """
    form_document = models.ForeignKey(FormDocument, related_name="shares_to_users")
    to_user = models.ForeignKey(User, related_name="shares_from_users")
    from_user = models.ForeignKey(User, null=True)

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
AUTO_SAVED = 6

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
