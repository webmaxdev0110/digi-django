from django.core.urlresolvers import reverse
from rest_framework.test import (
    APITestCase,
)

from contacts.constants import GenderSource
from contacts.models import Person
from identity_verification.constants import VerificationSource
from identity_verification.models import Passport


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
