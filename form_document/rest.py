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
from form_document.models import AUTO_SAVED


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

    def get_object_kwarg(self):
        request_action = self.request.data['request_action']
        form_document = None
        form_id = self.request.data['form_id']
        if form_id:
            form_document = FormDocument.objects.get(pk=form_id)
        kwargs = {}
        if form_document:
            kwargs['form_document'] = form_document
        if 'FORM_AUTOSAVE' == request_action:
            kwargs['status'] = AUTO_SAVED
        if self.request.user.is_authenticated():
            kwargs['receiver_user'] = self.request.user

        return kwargs

    def perform_create(self, serializer):
        kwargs = self.get_object_kwarg()
        inst = serializer.save(**kwargs)
        return inst


    def perform_update(self, serializer):
        kwargs = self.get_object_kwarg()
        inst = serializer.save(**kwargs)
        return inst
