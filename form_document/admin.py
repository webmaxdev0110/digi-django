from django.contrib import admin

from .models import FormDocument, FormDocumentUserShare, FormDocumentCompanyShare, FormDocumentSource, FormDocumentResponse


admin.site.register(FormDocument)
admin.site.register(FormDocumentUserShare)
admin.site.register(FormDocumentCompanyShare)
admin.site.register(FormDocumentSource)
admin.site.register(FormDocumentResponse)
