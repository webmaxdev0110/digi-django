from rest_framework.serializers import ModelSerializer

from .models import FormDocument


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
    class Meta:
        model = FormDocument
        fields = '__all__'

