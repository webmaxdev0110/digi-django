from django.http.request import split_domain_port
from django.utils.text import slugify
from rest_framework.serializers import (
    ModelSerializer,
    CurrentUserDefault,
    Serializer)
from rest_framework import serializers

from contacts.models import Person
from .models import (
    FormDocumentResponse,
    FormDocumentTemplate,
    FormDocumentResponseAttachment,
    FixedFormDocument,
    DocumentSignature)

from emails.apis import send_form_resume_link
try:
    # python 2
    from urlparse import urlparse
except ImportError:
    # Python 3
    from urllib.parse import urlparse



class FormDocumentTemplateListSerializer(ModelSerializer):
    created_by = serializers.ReadOnlyField(source='owner.get_full_name')
    status = serializers.ReadOnlyField(source='get_status_display')
    subdomain = serializers.CharField(source='owner.site.domain', read_only=True)
    class Meta:
        model = FormDocumentTemplate
        fields = (
            'id',
            'title',
            'slug',
            'created',
            'created_by',
            'status',
            'subdomain',
        )


class FormDocumentCreateSerializer(ModelSerializer):
    class Meta:
        model = FormDocumentTemplate
        fields = (
            'id',
            'title',
            'slug',
            'status',
            'uploaded_document',
            'form_data',
            'document_mapping',
            'form_config',
            'access_code',
        )
        extra_kwargs = {
            'title': {'write_only': True},
            'uploaded_document': {'write_only': True},
            'status': {'write_only': True},
            'form_data': {'write_only': True},
            'document_mapping': {'write_only': True},
            'form_config': {'write_only': True},
            'access_code': {'write_only': True}
        }

    def validate_slug(self, value):
        value = slugify(value)
        form_template_id = self.initial_data.get('id', None)
        exclude_filters = {}
        if form_template_id:
            exclude_filters = {'pk': self.initial_data['id']}

        if FormDocumentTemplate.objects.exclude(**exclude_filters).filter(slug=value).exists():
            raise serializers.ValidationError('Same URL exists')
        return value


class FormDocumentDetailSerializer(ModelSerializer):
    """
    FormDocumentDetailSerializer used to get details of Form
    """
    uploaded_document = serializers.FileField(write_only=True, required=False)
    assets_urls = serializers.SerializerMethodField()
    is_access_code_protected = serializers.BooleanField(read_only=True)
    form_data = serializers.SerializerMethodField()
    document_mapping = serializers.SerializerMethodField()
    subdomain = serializers.CharField(source='owner.site.domain', read_only=True)

    class Meta:
        model = FormDocumentTemplate
        fields = (
            'id',
            'title',
            'slug',
            'status',
            'uploaded_document',
            'form_data',
            'form_config',
            'document_mapping',
            'assets_urls',
            'is_access_code_protected',
            'subdomain',
        )

    def get_assets_urls(self, instance):
        if self._is_access_code_verified(instance):
            return map(lambda x: {
                # todo: Unit tests
                # This needs absolute uri, as our frontend server and backend server uses different port
                # Without absolute uri, the requests will be send to front-end address while it should
                # be in the backend
                'url': self.context['request'].build_absolute_uri(x.image.url),
                'width': x.cached_image_width,
                'height': x.cached_image_height,
            }, instance.form_assets.all())
        else:
            return None

    def _is_access_code_verified(self, instance):
        if self.instance.is_access_code_protected():
            user = CurrentUserDefault()
            if getattr(user, 'id', None) == instance.owner.id:
                return True
            if self.context['request'].query_params.get('access_code') == instance.access_code:
                return True
            else:
                return False
        else:
            return True


    def get_form_data(self, instance):
        if self._is_access_code_verified(instance):
            return instance.form_data
        return None

    def get_document_mapping(self, instance):
        if self._is_access_code_verified(instance):
            return instance.document_mapping
        return None


class FormDocumentLinkSerializer(Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(write_only=True)


class FixedFormDocumentSerializer(FormDocumentDetailSerializer):
    # Todo: rename to form_id
    id = serializers.IntegerField(source='template.pk')
    uploaded_document = serializers.FileField(write_only=True, required=False)
    assets_urls = serializers.SerializerMethodField()
    slug = serializers.SlugField(read_only=True, source='template.slug')
    is_access_code_protected = serializers.BooleanField(read_only=True)
    form_data = serializers.SerializerMethodField()
    document_mapping = serializers.SerializerMethodField()
    number_of_pages = serializers.IntegerField(source='template.number_of_pages')

    class Meta:
        model = FixedFormDocument
        fields = (
            'id',
            'slug',
            'title',
            'number_of_pages',
            'uploaded_document',
            'form_data',
            'form_config',
            'document_mapping',
            'assets_urls',
            'is_access_code_protected',
        )

    def get_assets_urls(self, instance):
        if self._is_access_code_verified(instance):
            return map(lambda x: {
                # todo: Unit tests
                # This needs absolute uri, as our frontend server and backend server uses different port
                # Without absolute uri, the requests will be send to front-end address while it should
                # be in the backend
                'url': self.context['request'].build_absolute_uri(x.image.url),
                'width': x.cached_image_width,
                'height': x.cached_image_height,
            }, instance.template.form_assets.all())
        else:
            return None

    def _is_access_code_verified(self, instance):
        if self.instance.template.is_access_code_protected():
            user = CurrentUserDefault()
            if getattr(user, 'id', None) == instance.template.owner.id:
                return True
            if self.context['request'].query_params.get('access_code') == instance.template.access_code:
                return True
            else:
                return False
        else:
            return True

    def get_form_data(self, instance):
        if self._is_access_code_verified(instance):
            return instance.form_data
        return None

    def get_document_mapping(self, instance):
        if self._is_access_code_verified(instance):
            return instance.document_mapping
        return None


class FormDocumentResponseAttachmentDetailSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(read_only=True, source='attachment_file_name')
    file_size = serializers.CharField(read_only=True, source='attachment.size')
    file_url = serializers.CharField(read_only=True, source='attachment.url')

    class Meta:
        model = FormDocumentResponseAttachment
        fields = (
            'file_name',
            'file_size',
            'file_url',
        )


class FormDocumentResponseSerializer(ModelSerializer):
    response_id = serializers.ReadOnlyField(source='pk')
    form_id = serializers.ReadOnlyField(source='form_document.pk')
    answers = serializers.JSONField()
    completion_percent = serializers.SerializerMethodField()
    completed_by_name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    duration_seconds = serializers.SerializerMethodField()
    contact_name = serializers.SerializerMethodField()
    contact_email = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()
    attachments = FormDocumentResponseAttachmentDetailSerializer(many=True, read_only=True)


    class Meta:
        model = FormDocumentResponse
        fields = (
            'response_id',
            'form_id',
            'created',
            'answers',
            'completion_percent',
            'completed_by_name',
            'status',
            'type',
            'duration_seconds',
            'contact_name',
            'contact_email',
            'contact_phone',
            'attachments',
        )

    def get_completion_percent(self, instance):
        cached_form = instance.cached_form
        try:
            return float(instance.get_num_of_completed_questions()) / cached_form.get_num_of_questions()
        except ZeroDivisionError:
            return 0


    def get_completed_by_name(self, instance):
        pass

    def get_type(self, instance):
        pass

    def get_duration_seconds(self, instance):
        pass

    def get_contact_name(self, instance):
        pass

    def get_contact_email(self, instance):
        pass

    def get_contact_phone(self, instance):
        pass


class FormResponseListSerializer(ModelSerializer):
    response_id = serializers.ReadOnlyField(source='pk')
    form_id = serializers.ReadOnlyField(source='form_document.pk')
    form_title = serializers.ReadOnlyField(source='form_document.title')
    completion_percent = serializers.SerializerMethodField()
    completed_by_name = serializers.SerializerMethodField()
    contact_email = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()


    class Meta:
        model = FormDocumentResponse
        fields = (
            'response_id',
            'form_id',
            'form_title',
            'created',
            'completion_percent',
            'completed_by_name',
            'status',
            'duration_seconds',
            'contact_email',
            'contact_phone',
        )


    def get_completion_percent(self, instance):
        pass

    def get_completed_by_name(self, instance):
        pass

    def get_contact_email(self, instance):
        pass

    def get_contact_phone(self, instance):
        pass

    def get_status(self, instance):
        return instance.get_status_display()


class FormDocumentResponseAttachmentCreateSerializer(serializers.ModelSerializer):

    response_id = serializers.IntegerField(required=False, write_only=True)
    form_id = serializers.IntegerField(required=False, write_only=True)
    file = serializers.FileField(required=True, write_only=True)
    file_name = serializers.ReadOnlyField(source='attachment_file_name')
    attachment_id = serializers.ReadOnlyField(source='pk')

    class Meta:
        model = FormDocumentResponseAttachment
        fields = (
            'response_id',
            'form_id',
            'file',
            'file_name',
            'attachment_id',
        )

    def validate_file(self, value):
        if len(value.name) > 100:
            raise serializers.ValidationError('File name exceeds 100 characters')
        return value

    def validate(self, attrs):
        form_id = attrs.get('form_id', None)
        response_id = attrs.get('response_id', None)
        if form_id is None and response_id is None:
            raise serializers.ValidationError('At least one of form_id or response_id is required')
        return attrs

    def create(self, validated_data):
        form_response = None
        response_id = validated_data.get('response_id')
        form_id = validated_data.get('form_id')
        if response_id:
            form_response = FormDocumentResponse.objects.get(pk=response_id)
        elif form_id:
            form = FormDocumentTemplate.objects.get(
                pk=form_id)
            cached_form = form.compile_form()
            form_response = cached_form.create_empty_response()
        assert isinstance(form_response, FormDocumentResponse)
        instance =  FormDocumentResponseAttachment.objects.create(
            attachment=validated_data['file'],
            response=form_response
        )
        return instance


class FormDocumentResponseResumeLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    response_id = serializers.IntegerField(required=True, write_only=True)
    form_continue_url = serializers.CharField(required=True)

    def validate(self, data):
        response_id = data.get('response_id')
        form_continue_url = data.get('form_continue_url')
        form_response  = FormDocumentResponse.objects.get(pk=response_id)
        subdomain = form_response.form_document.owner.site.domain
        netloc = urlparse(form_continue_url).netloc
        continue_url_origin, _= split_domain_port(netloc)
        if continue_url_origin == subdomain:
            return data
        else:
            raise serializers.ValidationError("Request origin does not match form continue origin")

    def create(self, validated_data):
        response_id = self.validated_data.get('response_id')
        form_response = FormDocumentResponse.objects.get(pk=response_id)
        form_title = form_response.form_document.title
        send_form_resume_link(
            validated_data['email'],
            validated_data['form_continue_url'],
            form_title
        )
        return validated_data

class FormDocumentSigningEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, write_only=True)
    response_id = serializers.IntegerField(required=True, write_only=True)
    code = serializers.CharField(required=False, write_only=True)
    display_name = serializers.CharField(required=False, write_only=True)
    is_verified = serializers.SerializerMethodField()

    def get_is_verified(self, inst):
        email = inst['email']
        response = FormDocumentResponse.objects.get(pk=inst['response_id'])
        signatures = DocumentSignature.objects.filter(
            content_type=response.get_ct(), object_id=response.pk
        )
        persons = [s.person for s in signatures]

        results = filter(lambda x: x.email == email and x.is_email_verified is True, persons)
        return len(results) > 0

    def send_email_verification_code(self):
        email = self.validated_data['email']
        display_name = self.validated_data['display_name']
        response = FormDocumentResponse.objects.get(
            pk=self.validated_data['response_id'])

        signatures = DocumentSignature.objects.filter(
            content_type=response.get_ct(), object_id=response.pk
        )
        person_query = signatures.filter(person__email=email)
        if not person_query.exists():
            person = Person.objects.create(
                email=email,
                display_name=display_name
            )
            signature = DocumentSignature.objects.create(
                content_type=response.get_ct(),
                object_id=response.pk,
                person=person
            )

            signature.save()
            person.send_email_verification_code()
        else:
            person_query.get().person.send_email_verification_code()

        return True

    def verify_email_code(self):
        email = self.validated_data['email']
        code = self.validated_data['code']
        response = FormDocumentResponse.objects.get(
            pk=self.validated_data['response_id'])
        signature = DocumentSignature.objects.filter(
            content_type=response.get_ct(), object_id=response.pk,
            person__email=email
        ).get()

        person = signature.person
        if person.verify_email_verification_code(code):
            person.set_email_verified()
