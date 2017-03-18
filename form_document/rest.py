from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.viewsets import GenericViewSet

from core.constants import StatusChoices
from core.hash_utils import sha1_file
from core.rest_pagination import get_pagination_class
from form_document.constants import FormCompletionStatus
from .models import (
    FormDocumentTemplate,
    FormDocumentResponse,
)
from .serializers import (
    FormDocumentSerializer,
    FormDocumentDetailSerializer,
    FormDocumentResponseSerializer,
    FormResponseListSerializer,
    FormDocumentCreateSerializer)



class FormDocumentRetrieveViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = FormDocumentTemplate.objects.all()
    serializer_class = FormDocumentDetailSerializer
    pagination_class = get_pagination_class(page_size=10)
    authentication_classes = []
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # get_current_site checks includes both port and non-port included search against Site table
        site = get_current_site(self.request)
        return FormDocumentTemplate.objects.filter(owner__site=site)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        try:
            val = int(self.kwargs['pk'])
            filter_kwargs = {'pk': self.kwargs['pk']}
        except ValueError:
            filter_kwargs = {'slug': self.kwargs['pk']}
        obj = get_object_or_404(queryset, **filter_kwargs)
        obj.get_or_create_compiled_form()
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class FormDocumentCreateUpdateViewSet(viewsets.ModelViewSet):
    queryset = FormDocumentTemplate.objects.all()
    pagination_class = get_pagination_class(page_size=10)
    parser_classes = (MultiPartParser, FormParser, JSONParser,)
    serializer_class = FormDocumentSerializer

    def get_object_kwarg(self):
        kwargs = {}
        if self.request.user.is_authenticated():
            kwargs['owner'] = self.request.user
        return kwargs

    def perform_create(self, serializer):
        kwargs = self.get_object_kwarg()
        document = serializer.validated_data.get('uploaded_document', None)
        if document:
            kwargs.update({
                'cached_sha1': sha1_file(document)
            })
        inst = serializer.save(**kwargs)
        inst.process_document()

    def perform_update(self, serializer):
        # Invalidate the cached_form
        inst = serializer.save(**{'cached_form': None})
        return inst

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        elif self.action == 'create' or self.action == 'update':
            return FormDocumentCreateSerializer


class FormDocumentResponseViewSet(viewsets.ModelViewSet):
    queryset = FormDocumentResponse.objects
    serializer_class = FormDocumentResponseSerializer
    # Below authentication_classes is necessary for Django browsable API view
    authentication_classes = (SessionAuthentication,)
    pagination_class = get_pagination_class(page_size=10)
    filter_backends = (OrderingFilter,)
    ordering_fields = (
        'id',
        'duration_seconds',
        'status',
    )

    def get_serializer_class(self):
        if self.action == 'list':
            return FormResponseListSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        # All the forms owned by this user
        owned_form_ids = FormDocumentTemplate.objects.filter(
            owner=self.request.user).values_list('id', flat=True)
        # All the forms shared to this user
        # todo: 1. FormDocumentTemplate shared to entire company
        # todo: 2. FormDocumentTemplate shared by one user
        return FormDocumentResponse.objects.filter(
            form_document__id__in=owned_form_ids
        )

    def get_object_kwarg(self):
        request_action = self.request.data['request_action']
        form_document = None
        form_id = self.request.data['form_id']
        if form_id:
            form_document = FormDocumentTemplate.objects.get(pk=form_id)
        kwargs = {}
        if form_document:
            kwargs['form_document'] = form_document
        if 'FORM_AUTOSAVE' == request_action:
            kwargs['status'] = FormCompletionStatus.AUTO_SAVED
        if self.request.user.is_authenticated():
            kwargs['receiver_user'] = self.request.user

        return kwargs

    def perform_create(self, serializer):
        kwargs = self.get_object_kwarg()
        # Check if the cached_form points to null, create a copy
        form_document_template = kwargs.get('form_document')
        form_document_template.get_or_create_compiled_form()
        inst = serializer.save(**kwargs)
        return inst

    def perform_update(self, serializer):
        kwargs = self.get_object_kwarg()
        inst = serializer.save(**kwargs)
        return inst
