from django.contrib import admin

from .models import FormDocument, FormDocumentUserShare, FormDocumentCompanyShare, FormDocumentResponse


admin.site.register(FormDocument)
admin.site.register(FormDocumentUserShare)
admin.site.register(FormDocumentCompanyShare)
admin.site.register(FormDocumentResponse)
