from rest_framework.serializers import (
    ModelSerializer,
    CurrentUserDefault,
)
from rest_framework import serializers

from .models import FormDocument, FormDocumentResponse


class FormDocumentSerializer(ModelSerializer):
    class Meta:
        model = FormDocument
        fields = (
            'id',
            'title',
            'slug',
            'created',
        )


class FormDocumentDetailSerializer(ModelSerializer):
    """
    FormDocumentDetailSerializer used to get details of Form
    """
    uploaded_document = serializers.FileField(write_only=True, required=False)
    assets_urls = serializers.SerializerMethodField()
    is_access_code_protected = serializers.BooleanField()
    form_data = serializers.SerializerMethodField()
    document_mapping = serializers.SerializerMethodField()

    class Meta:
        model = FormDocument
        fields = (
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
                'url': x.image.url,
                'width': x.image.width,
                'height': x.image.height,
            }, instance.form_assets.all())
        else:
            return None

    def _is_access_code_verified(self, instance):
        if self.instance.is_access_code_protected():
            user = CurrentUserDefault()
            if user and user.id == instance.owner.id:
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

    class Meta:
        model = FormDocumentResponse
        fields = (
            'response_id',
            'form_id',
            'answers',
        )
