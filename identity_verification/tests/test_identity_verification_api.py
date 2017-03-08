from django.core.urlresolvers import reverse
from rest_framework.test import (
    APITestCase,
)

from contacts.constants import GenderSource
from contacts.models import Person
from identity_verification.constants import VerificationSource
from identity_verification.models import (
    Passport,
    PersonVerificationAttachment,
    DriverLicense,
)
from django.core.files.uploadedfile import SimpleUploadedFile

class IdentityVerificationRestAPITestCase(APITestCase):

    def test_verify_dvs_passport(self):
        url = reverse('api_identity_verification:identify-list')
        self.assertEqual(Passport.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        actual = self.client.post(
            url,
            {
                'type': VerificationSource.DVSPASSPORT,
                'verification_data': {
                    'passport': {
                        'number': 'G0000000',
                        'expiry_date': '2013-10-30',
                        'place_of_birth': 'Sydney',
                        'country': 'AU'
                    }
                },
                'person': {
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'date_of_birth': '1989-08-01',
                    'email': 'test@example.com',
                    'gender': GenderSource.Male,
                    'mobile_number': '0000001'
                }
            },
            format='json')
        excepted = {
            'result': False
        }
        self.assertEqual(Passport.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 1)
        self.assertDictContainsSubset(excepted, actual.json())

    def test_verify_dvs_driver_license(self):
        url = reverse('api_identity_verification:identify-list')
        self.assertEqual(DriverLicense.objects.count(), 0)
        self.assertEqual(Person.objects.count(), 0)

        actual = self.client.post(
            url,
            {
                'type': VerificationSource.DVSDRIVERLICENSE,
                'verification_data': {
                    'driver_license': {
                        'number': '076310691',
                        'state': 'VIC',
                    }
                },
                'person': {
                    'first_name': 'John',
                    'last_name': 'Smith',
                    'date_of_birth': '1983-03-05'
                }
            },
            format='json')
        excepted = {
            'result': True
        }
        self.assertEqual(DriverLicense.objects.count(), 1)
        self.assertEqual(Person.objects.count(), 1)
        self.assertDictContainsSubset(excepted, actual.json())

    def test_upload_identification_document(self):
        num_of_identification_document = PersonVerificationAttachment.objects.count()
        url = reverse('api_identity_verification:identify-attachment-list')
        pdf_file = SimpleUploadedFile("file.pdf", "file_content", content_type='application/pdf')
        response = self.client.post(url, {
            'file': pdf_file
        }, format='multipart')
        self.assertEqual(response.status_code, 201)
        expected_key = 'id'
        self.assertIn(expected_key, response.json())
        self.assertEqual(num_of_identification_document+1, PersonVerificationAttachment.objects.count())

    def test_linking_identification_document(self):
        """
        Given one PersonVerificationAttachment object,
        link it to a person
        """
        url = reverse('api_identity_verification:identify-list')
        person = Person.objects.create(first_name='John', last_name='smith')
        pdf_file = SimpleUploadedFile("file.pdf", "file_content", content_type='application/pdf')
        attachment1 = PersonVerificationAttachment.objects.create(file=pdf_file)
        attachment2 = PersonVerificationAttachment.objects.create(file=pdf_file)

        response = self.client.post(
            url,
            {
                'type': VerificationSource.MANUAL_FILE_UPLOAD,
                'person': {
                    'id': person.id
                },
                'attachment_ids': [attachment1.id, attachment2.id]
            },
            format='json')

        self.assertIsNotNone(PersonVerificationAttachment.objects.get(pk=attachment1.id).verification)
        self.assertIsNotNone(PersonVerificationAttachment.objects.get(pk=attachment2.id).verification)

        excepted = {
            'result': True
        }
        self.assertDictContainsSubset(excepted, response.json())