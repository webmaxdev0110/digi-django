from rest_framework import viewsets

from core.rest_pagination import get_pagination_class
from .models import FormDocument
from .serializers import FormDocumentSerializer, FormDocumentDetailSerializer


class FormDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FormDocument.objects.all()
    serializer_class = FormDocumentSerializer
    pagination_class = get_pagination_class(page_size=10)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FormDocumentDetailSerializer
        return self.serializer_class

