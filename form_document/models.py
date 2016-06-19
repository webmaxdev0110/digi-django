from __future__ import unicode_literals

from django.core.files.temp import NamedTemporaryFile
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import (
    JSONField,
    ArrayField,
)
from django.contrib.sites.models import Site
from django.db import models
from storages.backends.gs import GSBotoStorage
from wand.image import Image
from wand.color import Color
from accounts.models import User, Company
from core.models import TimeStampedModel
import os
import pyPdf
from form_document.pdf import ConvertToImage
from form_document.pdf2 import convert
from django.core.files import File

def document_path_dir(instance, filename):
    file_name_no_extension = os.path.splitext(filename)[0]
    return 'documents/users/{0}/{1}'.format(
        instance.owner.pk,
        file_name_no_extension,
    )

def document_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename
    dir_name = document_path_dir(instance, filename)
    return '{0}/{1}'.format(
        dir_name,
        filename,
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
    form_data = JSONField(null=True)      # All the form data
    document_mapping = ArrayField(
        JSONField(),
        null=True
    )
    form_config = JSONField(null=True)

    owner = models.ForeignKey(User, help_text='The owner of this document')
    site = models.ForeignKey(Site)

    def __unicode__(self):
        return '<FormDocument: {0}>'.format(self.title[:16])

    class Meta:
        verbose_name = 'Form'
        verbose_name_plural = 'Forms'

    def process_document(self):
        if self.uploaded_document:
            original_document = NamedTemporaryFile(delete=False)
            self.uploaded_document.seek(0)
            for chunk in self.uploaded_document.chunks():
                original_document.write(chunk)
            original_document.close()

            number_of_pages = 0
            with open(original_document.name, 'rb') as original_document_file:
                pdf = pyPdf.PdfFileReader(original_document_file)
                number_of_pages = pdf.getNumPages()
            # todo: Resolution can be decided depending on
            # the size of the document

            if number_of_pages > 0:
                generated_image_paths = []
                for page in range(number_of_pages):
                    with Image(filename=original_document.name+'[{0}]'.format(page), resolution=75) as img:
                        img_file = NamedTemporaryFile(delete=False, suffix='png')
                        img.alpha_channel = False
                        img.save(filename=img_file.name)
                        generated_image_paths.append(img_file.name)

                for image_path in generated_image_paths:
                    with open(image_path, 'r') as image_file:
                        form_asset = FormDocumentAssets(form_document=self, image=File(image_file))
                        form_asset.save()


    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(FormDocument, self).save(force_insert, force_update, using, update_fields)
        self.process_document()


class FormDocumentAssets(models.Model):
    form_document = models.ForeignKey(FormDocument)
    image = models.ImageField(upload_to=document_path, storage=documents_store)


class FormDocumentCompanyShare(TimeStampedModel):
    """
    FormDocumentCompanyShare represents a document to be shared
    within the user's company or to another company

    """
    form_document = models.ForeignKey(FormDocument)
    from_company = models.ForeignKey(Company, related_name='forms_shared_to_other_companies')
    to_company = models.ForeignKey(Company, related_name='forms_received_from_other_companies')
    company_visible = models.BooleanField(
        default=False,
        help_text='If company visible is not true, only the compnay admin can view the document')

    class Meta:
        unique_together = (('form_document', 'to_company'),)
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
    form_document = models.ForeignKey(FormDocument, related_name='forms_shared_to_other_users')
    to_user = models.ForeignKey(User, related_name='forms_received_from_other_users')
    from_user = models.ForeignKey(User, null=True)

    class Meta:
        unique_together = (('form_document', 'to_user'),)
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


# todo: Move to constant file
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
    (AUTO_SAVED, _('Auto Saved')),
)

class FormDocumentResponse(TimeStampedModel):
    """
    FormDocumentResponse represents Form submission per User
    When form is published, users registered to platform or anonymous users can submit form

    """
    receiver_user = models.ForeignKey(
        User, null=True,
        help_text='The user who submitted the form, optional',
        related_name='all_form_responses'
    )
    sender_user = models.ForeignKey(
        User, null=True,
        help_text='The user who submitted the form, optional',
        related_name='all_forms_sent'
    )
    last_interactive_timestamp = models.DateTimeField(auto_now=True)
    form_document = models.ForeignKey(FormDocument)
    answers = JSONField()
    status = models.SmallIntegerField(choices=FORM_COMPLETION_STATUS, default=UNOPENED)

    class Meta:
        verbose_name = 'FormResponse'
        verbose_name_plural = 'FormResponses'


class FormDocumentResponseUserPermission(TimeStampedModel):
    from_user = models.ForeignKey(User, related_name='forms_responses_shared_to_other_users')
    to_user = models.ForeignKey(User, related_name='form_responses_received_from_other_users')
    response = models.ForeignKey(FormDocumentResponse)


class FormDocumentResponseCompanyPermission(TimeStampedModel):
    from_company = models.ForeignKey(Company, related_name='+')
    to_company = models.ForeignKey(Company, related_name='+')
    response = models.ForeignKey(FormDocumentResponse)


class FormDocumentLink(TimeStampedModel, DocumentRecipient):
    """
    Model to track document recipient whether or not opened
    the form or not
    """
    form_response = models.OneToOneField(FormDocumentResponse, null=True)
    from_user = models.ForeignKey(User)
    hash = models.CharField(max_length=128)
