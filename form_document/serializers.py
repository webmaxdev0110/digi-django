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

    def get_assets_urls(self, instance):
        return map(lambda x: x.image.url, instance.form_assets.all())

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
        )




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
