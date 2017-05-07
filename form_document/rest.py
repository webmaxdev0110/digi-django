from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import (
    MultiPartParser,
    FormParser,
    JSONParser,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from core.hash_utils import sha1_file
from core.rest_pagination import get_pagination_class
from core.site_utils import get_site_from_request_origin
from form_document.apis import email_trackable_form_submission_link
from form_document.constants import FormCompletionStatus
from .models import (
    FormDocumentTemplate,
    FormDocumentResponse,
)
from .serializers import (
    FormDocumentTemplateListSerializer,
    FormDocumentDetailSerializer,
    FormDocumentResponseSerializer,
    FormResponseListSerializer,
    FormDocumentCreateSerializer,
    FormDocumentResponseAttachmentCreateSerializer,
    FormDocumentResponseResumeLinkSerializer,
    FixedFormDocumentSerializer,
    FormDocumentSigningEmailVerificationSerializer,
    FormDocumentLinkSerializer)


class FormDocumentRetrieveViewSet(mixins.RetrieveModelMixin, GenericViewSet):
    queryset = FormDocumentTemplate.objects.all()
    serializer_class = FixedFormDocumentSerializer
    pagination_class = get_pagination_class(page_size=10)
    authentication_classes = []
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # We should get the site from request origin
        # not from request host
        # Frontend url is different to backend
        site = get_site_from_request_origin(self.request)
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

        # Should use the cached_form in the response
        return obj.cached_form


class FormDocumentViewSet(viewsets.ModelViewSet):
    queryset = FormDocumentTemplate.objects.available()
    pagination_class = get_pagination_class(page_size=10)
    parser_classes = (MultiPartParser, FormParser, JSONParser,)
    serializer_class = FormDocumentTemplateListSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = (
        'id',
        'title',
        'slug',
        'created',
        'status',
    )

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
        else:
            return FormDocumentDetailSerializer

    @detail_route(methods=['post'])
    def email_form_tracking_link(self, request, pk=None):
        serializer = FormDocumentLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = get_object_or_404(FormDocumentTemplate.objects, **{'pk': pk})
        email_trackable_form_submission_link(
            document,
            serializer.validated_data['email'],
            request.user,
            serializer.validated_data.get('first_name', None)
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK, headers=headers)

    @detail_route(methods=['delete'])
    def archive(self, request, pk=None):
        document = get_object_or_404(FormDocumentTemplate.objects, **{'pk': pk})
        document.archive()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['post'])
    def duplicate(self, request, pk=None):
        document = get_object_or_404(FormDocumentTemplate.objects, **{'pk': pk})
        new_document = document.duplicate()

        return Response({
            'id': new_document.pk
        }, status=status.HTTP_201_CREATED)


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
        if self.action == 'update':
            return FormDocumentResponse.objects.filter(id=self.request.data['session_id'])
        elif self.action == 'retrieve':
            # todo: Security check! If the form is closed, remove the public access
            return FormDocumentResponse.objects.filter(id=self.kwargs['pk'])
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

    def get_permissions(self):
        # todo: Security review
        if self.action == 'create' or self.action == 'update' or self.action == 'retrieve':
            return (AllowAny(),)
        else:
            return super(FormDocumentResponseViewSet, self).get_permissions()

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def upload_attachment(self, request, *args, **kwargs):
        serializer = FormDocumentResponseAttachmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def send_resume_link(self, request, *args, **kwargs):
        serializer = FormDocumentResponseResumeLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        kwargs = self.get_object_kwarg()
        # Check if the cached_form points to null, create a copy
        form_document_template = kwargs.get('form_document')
        cached_form = form_document_template.get_or_create_compiled_form()
        kwargs.update({
            'cached_form': cached_form
        })
        inst = serializer.save(**kwargs)
        return inst

    def perform_update(self, serializer):
        kwargs = self.get_object_kwarg()
        inst = serializer.save(**kwargs)
        return inst


class SigningVerificationViewSet(GenericViewSet):
    serializer_class = FormDocumentSigningEmailVerificationSerializer
    queryset = FormDocumentResponse.objects

    @list_route(methods=['get'], permission_classes=(AllowAny,))
    def check_email(self, request):
        s = FormDocumentSigningEmailVerificationSerializer(data=request.GET)
        s.is_valid(raise_exception=True)

        return Response(
            s.data,
            status=status.HTTP_200_OK)

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def request_email_verification_code(self, request):
        s = FormDocumentSigningEmailVerificationSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.send_email_verification_code()
        return Response(status=status.HTTP_200_OK)

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def verify_email_code(self, request):
        s = FormDocumentSigningEmailVerificationSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.verify_email_code()
        return Response(data=s.data,
                        status=status.HTTP_200_OK)
