from django.utils.text import slugify
from rest_framework.serializers import (
    ModelSerializer,
    CurrentUserDefault,
)
from rest_framework import serializers

from .models import (
    FormDocumentResponse,
    FormDocumentTemplate,
    FormDocumentResponseAttachment,
)


class FormDocumentTemplateListSerializer(ModelSerializer):
    class Meta:
        model = FormDocumentTemplate
        fields = (
            'id',
            'title',
            'slug',
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
        if FormDocumentTemplate.objects.filter(slug=value, owner=self.context['request'].user).exists():
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

    class Meta:
        model = FormDocumentTemplate
        fields = (
            'id',
            'title',
            'slug',
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




class FormDocumentResponseSerializer(ModelSerializer):
    response_id = serializers.ReadOnlyField(source='pk')
    form_id = serializers.ReadOnlyField(source='form_document.pk')
    answers = serializers.JSONField()
    completion_percent = serializers.SerializerMethodField()
    completed_by_name = serializers.SerializerMethodField()
    sent_channel = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    duration_seconds = serializers.SerializerMethodField()
    contact_email = serializers.SerializerMethodField()
    contact_phone = serializers.SerializerMethodField()


    class Meta:
        model = FormDocumentResponse
        fields = (
            'response_id',
            'form_id',
            'created',
            'answers',
            'completion_percent',
            'completed_by_name',
            'sent_channel',
            'status',
            'type',
            'duration_seconds',
            'contact_email',
            'contact_phone',
        )


    def get_completion_percent(self, instance):
        pass

    def get_completed_by_name(self, instance):
        pass

    def get_sent_channel(self, instance):
        pass

    def get_type(self, instance):
        pass

    def get_duration_seconds(self, instance):
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
    sent_channel = serializers.SerializerMethodField()
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
            'sent_channel',
            'status',
            'duration_seconds',
            'contact_email',
            'contact_phone',
        )


    def get_completion_percent(self, instance):
        pass

    def get_completed_by_name(self, instance):
        pass

    def get_sent_channel(self, instance):
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
