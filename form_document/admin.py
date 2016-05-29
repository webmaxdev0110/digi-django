from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.forms import ModelForm, forms

from .models import FormDocument, FormDocumentUserShare, FormDocumentCompanyShare, FormDocumentResponse


class FormDocumentAdminForm(ModelForm):
    uploaded_document = forms.FileField(widget=AdminFileWidget, required=False)


class FormDocumentAdmin(admin.ModelAdmin):
    form = FormDocumentAdminForm



admin.site.register(FormDocument, FormDocumentAdmin)
admin.site.register(FormDocumentUserShare)
admin.site.register(FormDocumentCompanyShare)
admin.site.register(FormDocumentResponse)
