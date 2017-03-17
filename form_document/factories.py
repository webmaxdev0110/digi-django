import factory
from django.core.files.base import ContentFile

from accounts.factories import UserFactory
from form_document.models import FormDocumentTemplate


class FormDocumentTemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = FormDocumentTemplate

    title = factory.sequence(lambda n: 'Form <%d>' % n)
    slug = factory.sequence(lambda n: 'slug-%d' % n)
    uploaded_document = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.FileField()._make_data(
                {'data': '12'}
            ), 'example.pdf'
        )
    )
    form_data = {
        'questions': 'test'
    }
    document_mapping = {}
    form_config = {}
    owner = factory.SubFactory(UserFactory)
    access_code = None
