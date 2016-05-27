from rest_framework import viewsets

from core.rest_pagination import get_pagination_class
from .models import FormDocument
from .serializers import FormDocumentSerializer


class FormDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FormDocument.objects.all()
    serializer_class = FormDocumentSerializer
    pagination_class = get_pagination_class(page_size=10)
