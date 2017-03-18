from __future__ import unicode_literals
import ntpath

from django.core.files.temp import NamedTemporaryFile
from django.contrib.postgres.fields import (
    JSONField,
)
from django.db import models
from wand.image import Image
from accounts.models import User, Company
from core.models import TimeStampedModel, StatusModel
import os
import pyPdf
from django.core.files import File

from core.core_storages import (
    owner_document_path,
    get_document_storage,
)
from form_document.constants import (
    FORM_SENDING_METHOD_CHOICES,
    FormSendingMethod,
    FORM_COMPLETION_STATUS,
    FormCompletionStatus,
)


def form_document_template_uploaded_document_path(instance, filename):
    # documents/users/<user_pk>/<template_id>/uploaded_document/file_name.ext
    dir_name = owner_document_path('documents', instance.owner.pk)
    relative_path = os.path.join('uploaded_document', filename)
    return os.path.join(dir_name, relative_path)


class FormDocumentTemplate(TimeStampedModel, StatusModel):
    """
    Represents a form document created by an user
    The form should be accessible by document owner,
    owner's organisation account admin
    """

    title = models.CharField(max_length=256, default='Untitled Form')
    slug = models.SlugField(blank=True, help_text='Use for short URL sharing')
    uploaded_document = models.FileField(
        null=True,
        upload_to=form_document_template_uploaded_document_path,
        storage=get_document_storage(),
        max_length=255,
        help_text='The document uploaded used for populating after a form is completed')
    form_data = JSONField(null=True)      # All the form data
    # example {1: {type:'standard', positions:[bbox:[0, 0, 10, 10], page:1]}}
    document_mapping = JSONField(default={})
    cached_form = models.ForeignKey('FixedFormDocument', null=True)

    form_config = JSONField(null=True)
    access_code = models.CharField(max_length=4, null=True)
    owner = models.ForeignKey(User, help_text='The owner of this document')
    cached_sha1 = models.CharField(max_length=40, blank=True)

    def __unicode__(self):
        return '<FormDocumentTemplate: {0}>'.format(self.title[:16])

    class Meta:
        verbose_name = 'FormTemplate'
        verbose_name_plural = 'FormTemplates'

    def get_or_create_compiled_form(self):
        if not self.cached_form:
            fixed_form = self.compile_form()
            self.cached_form = fixed_form
            self.save()

        return self.cached_form


    def compile_form(self):
        return FixedFormDocument.objects.create(
            title=self.title,
            uploaded_document=self.uploaded_document,
            form_data=self.form_data,
            document_mapping=self.document_mapping,
            form_config=self.form_config,
            template=self
        )

    def is_access_code_protected(self):
        return self.access_code is not None

    def process_document(self):
        if self.uploaded_document:
            self.form_assets.all().delete()
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
                    with Image(filename=original_document.name+'[{0}]'.format(page), resolution=90) as img:
                        img_file = NamedTemporaryFile(delete=False, suffix='_{0}.png'.format(page))
                        img.alpha_channel = False
                        img.save(filename=img_file.name)
                        generated_image_paths.append(img_file.name)
                for i, image_path in enumerate(generated_image_paths):
                    with open(image_path, 'r') as image_file:
                        form_asset = FormDocumentTemplateDocumentPreview.objects.create(
                            form_document=self,
                            image=File(image_file),
                            order=i
                        )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        super(FormDocumentTemplate, self).save(force_insert, force_update, using, update_fields)


def form_document_cached_document_path(instance, filename):
    # documents/users/<user_pk>/<template_id>/history/<FixedFormDocument_id>/file_name.ext
    user = instance.template.owner
    dir_name = owner_document_path('documents', user.pk)
    relative_path = os.path.join(str(instance.template.pk), 'history', str(instance.pk), filename)
    return os.path.join(dir_name, relative_path)


class FixedFormDocument(TimeStampedModel):
    """
    This model represents a copy form used for populate document
    It allows user to update existing Form without breaking
    already published form
    """
    title = models.CharField(max_length=256, default='Untitled Form')
    uploaded_document = models.FileField(
        null=True,
        upload_to=form_document_cached_document_path,
        storage=get_document_storage(),
        max_length=255,
        help_text='The document uploaded used for populating after a form is completed')
    form_data = JSONField(null=True)  # All the form data
    # example {1: {type:'standard', positions:[bbox:[0, 0, 10, 10], page:1]}}
    document_mapping = JSONField(default={})
    form_config = JSONField(null=True)
    template = models.ForeignKey(FormDocumentTemplate)


def form_document_template_uploaded_document_preview_path(instance, file_path):
    # documents/users/<user_pk>/<template_id>/previews/file_name.ext
    form_document = instance.form_document
    dir_name = owner_document_path('documents', form_document.owner.pk)
    relative_path = os.path.join(str(form_document.pk), 'previews', ntpath.basename(file_path))
    return os.path.join(dir_name, relative_path)

class FormDocumentTemplateDocumentPreview(models.Model):
    form_document = models.ForeignKey(FormDocumentTemplate, related_name='form_assets')
    image = models.ImageField(
        upload_to=form_document_template_uploaded_document_preview_path, storage=get_document_storage(),
        height_field='cached_image_height',
        width_field='cached_image_width'
    )
    order = models.SmallIntegerField(default=0)
    cached_image_width = models.IntegerField(null=True)
    cached_image_height = models.IntegerField(null=True)

    class Meta:
        ordering = ["order"]

    @property
    def owner(self):
        return self.form_document.owner


class FormDocumentCompanyShare(TimeStampedModel):
    """
    FormDocumentCompanyShare represents a document to be shared
    within the user's company or to another company

    """
    form_template = models.ForeignKey(FormDocumentTemplate)
    from_company = models.ForeignKey(Company, related_name='forms_shared_to_other_companies')
    to_company = models.ForeignKey(Company, related_name='forms_received_from_other_companies')
    company_visible = models.BooleanField(
        default=False,
        help_text='If company visible is not true, only the compnay admin can view the document')

    class Meta:
        unique_together = (('form_template', 'to_company'),)
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
    form_template = models.ForeignKey(FormDocumentTemplate, related_name='forms_shared_to_other_users')
    to_user = models.ForeignKey(User, related_name='forms_received_from_other_users')
    from_user = models.ForeignKey(User, null=True)

    class Meta:
        unique_together = (('form_template', 'to_user'),)
        verbose_name = 'FormUserShare'
        verbose_name_plural = 'FormUserShares'


class DocumentRecipient(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    access_code = models.CharField(max_length=12)

    class Meta:
        abstract = True


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
    duration_seconds = models.IntegerField(default=0)
    form_document = models.ForeignKey(FormDocumentTemplate)
    answers = JSONField()
    status = models.SmallIntegerField(choices=FORM_COMPLETION_STATUS, default=FormCompletionStatus.UNOPENED)

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
    sending_method = models.IntegerField(
        choices=FORM_SENDING_METHOD_CHOICES, default=FormSendingMethod.DIRECT
    )
    hash = models.CharField(max_length=128)
