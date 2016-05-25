from rest_framework import viewsets

from core.rest_pagination import get_pagination_class
from form_document.models import FormDocument
from form_document.serializers import FormDocumentSerializer


class FormDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    model = FormDocument
    serializer_class = FormDocumentSerializer
    pagination_class = get_pagination_class(page_size=10)

    def get_queryset(self):
        queryset = super(FormDocumentViewSet, self).get_queryset()



    def filter_queryset(self, queryset):
        pass


