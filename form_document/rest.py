from rest_framework import viewsets
from rest_framework.response import Response

from core.rest_pagination import get_pagination_class
from .models import (
    FormDocument,
    FormDocumentResponse,
)
from .serializers import (
    FormDocumentSerializer,
    FormDocumentDetailSerializer,
    FormDocumentResponseSerializer,
)


class FormDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FormDocument.objects.all()
    serializer_class = FormDocumentSerializer
    pagination_class = get_pagination_class(page_size=10)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FormDocumentDetailSerializer
        return self.serializer_class

    def get_form_response(self, response_id):
        # get FormDocumentResponse object
        try:
            form_response = FormDocumentResponse.objects.get(id=response_id)
        except FormDocumentResponse.DoesNotExist:
            return None
        serializer = FormDocumentResponseSerializer(form_response)
        return serializer.data

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if self.request.query_params.get('session_id', None):
            form_response = self.get_form_response(int(self.request.query_params.get('session_id')))
            # it's required to check if response is related with form
            response = serializer.data
            if form_response and form_response['form'] == response['id']:
                response.update({'form_response': form_response})
                return Response(response)
        return Response(serializer.data)


class FormDocumentResponseViewSet(viewsets.ModelViewSet):
    queryset = FormDocumentResponse.objects
    serializer_class = FormDocumentResponseSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)