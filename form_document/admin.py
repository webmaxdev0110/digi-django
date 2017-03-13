from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.forms import ModelForm
from django import forms


from .models import FormDocumentTemplate, FormDocumentUserShare, FormDocumentCompanyShare, FormDocumentResponse, \
    FormDocumentAsset


class FormDocumentTemplateAdminForm(ModelForm):
    uploaded_document = forms.FileField(widget=AdminFileWidget, required=False)
    access_code = forms.CharField(required=False)


class FormDocumentTemplateAdmin(admin.ModelAdmin):
    form = FormDocumentTemplateAdminForm
    readonly_fields = (
        'document_mapping',
        'form_config',
    )



admin.site.register(FormDocumentTemplate, FormDocumentTemplateAdmin)
admin.site.register(FormDocumentUserShare)
admin.site.register(FormDocumentCompanyShare)
admin.site.register(FormDocumentResponse)
