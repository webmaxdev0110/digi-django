import factory
from django.core.files.base import ContentFile

from accounts.factories import UserFactory
from form_document.constants import FormCompletionStatus
from form_document.models import (
    FormDocumentTemplate,
    FormDocumentResponse,
)


class SimpleFormDocumentTemplateFactory(factory.DjangoModelFactory):
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


class ApplicationFormDocumentTemplateFactory(factory.DjangoModelFactory):
    class Meta:
        model = FormDocumentTemplate

    title = factory.sequence(lambda n: 'Application Form <%d>' % n)
    slug = factory.sequence(lambda n: 'application-form-%d' % n)
    uploaded_document = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.FileField()._make_data(
                {'data': '12'}
            ), 'example.pdf'
        )
    )
    form_data = {
        "questions": [{
            "type": "Group",
            "id": 0,
            "title": "Basic Information"
        }, {
            "group": 0,
            "validations": [{
                "type": "isRequired"
            }, {
                "type": "minLength",
                "value": 2
            }, {
                "type": "maxLength",
                "value": 20
            }],
            "type": "ShortTextField",
            "id": 1,
            "question_instruction": "What is your name?"
        }, {
            "group": 0,
            "validations": [{
                "type": "isRequired"
            }],
            "type": "SignatureField",
            "id": 2,
            "question_instruction": "Sign your name"
        }, {
            "group": 0,
            "validations": [{
                "type": "isRequired"
            }, {
                "type": "minimum",
                "value": 10
            }, {
                "type": "maximum",
                "value": 99
            }],
            "type": "NumberField",
            "id": 3,
            "question_instruction": "Hi {{answer_1}} How old are you?"
        }, {
            "group": 0,
            "type": "LongTextField",
            "id": 4,
            "question_instruction": "You only see this question if you are older than 20"
        }, {
            "group": 0,
            "include_other": True,
            "validations": [{
                "type": "isRequired"
            }],
            "question_instruction": "What is the value of your savings and investments?",
            "choices": [{
                "text": "$1,000,000+",
                "label": "A"
            }, {
                "text": "$200k - 900k",
                "label": "B"
            }],
            "type": "MultipleChoice",
            "id": 5
        }, {
            "type": "Group",
            "id": 6,
            "title": "Trust Details"
        }, {
            "group": 6,
            "validations": [{
                "type": "isRequired"
            }],
            "type": "PhoneNumberField",
            "id": 7,
            "question_instruction": "What is your phone number?"
        }, {
            "group": 6,
            "validations": [{
                "type": "isRequired"
            }],
            "question_instruction": "Choose an item from dropdown",
            "choices": ["Dropdown Item 1", "Dropdown Item 2", "Dropdown Item 3"],
            "type": "DropdownField",
            "id": 8
        }, {
            "group": 6,
            "validations": [{
                "type": "isRequired"
            }],
            "type": "YesNoChoiceField",
            "id": 9,
            "question_instruction": "Are you married?"
        }, {
            "date_format": "DD/MM/YYYY",
            "group": 6,
            "validations": [{
                "type": "isRequired"
            }],
            "question_instruction": "What is your date of birth?",
            "type": "DateField",
            "id": 10
        }, {
            "group": 6,
            "validations": [{
                "type": "isRequired"
            }],
            "max_answers": 2,
            "choices": [{
                "text": "$1,000,000+",
                "label": "A"
            }, {
                "text": "$200k - 900k",
                "label": "B"
            }, {
                "text": "$900k - 1900k",
                "label": "C"
            }, {
                "text": "$1900k - 2900k",
                "label": "D"
            }],
            "question_instruction": "What is the value of your savings and investments?",
            "allow_multiple": True,
            "type": "MultipleChoice",
            "id": 11
        }]
    }
    document_mapping = {}
    form_config = {}
    owner = factory.SubFactory(UserFactory)
    access_code = None


class ApplicationFormResponseFactory(factory.DjangoModelFactory):
    class Meta:
        model = FormDocumentResponse

    sender_user = factory.SubFactory(UserFactory)
    duration_seconds = 100
    answers = [
        {
            'id': 1,
            'value': 'John'
        }
    ]
    status = FormCompletionStatus.SAVED
