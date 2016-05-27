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
