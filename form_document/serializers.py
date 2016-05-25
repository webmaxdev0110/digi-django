from rest_framework.serializers import ModelSerializer

from form_document.models import FormDocument




class FormDocumentSerializer(ModelSerializer):
    class Meta:
        model = FormDocument
        fields = (
            'title',
            'slug',
            'form_data'
        )
