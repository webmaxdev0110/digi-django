import requests
from contacts.models import (
    Person,
    Location,
)
from identity_verification.constants import (
    VerificationSource,
    DVS_SOURCE_SET,
)
from identity_verification.models import (
    DriverLicense,
    Passport,
    MedicareCard,
)
from django.conf import settings

CONSENT_MAP = {
    VerificationSource.DVSPASSPORT : 'DVS Passport Search',
    VerificationSource.DVSDRIVERLICENSE: 'DVS Driver License Search',
    VerificationSource.DVSMEDICARECARD: 'DVS Medicare Search'
}


class TruliooRequestBuilder(object):
    """
    The request builder for using trulioo API
    """
    def __init__(self, person=None, passport=None,
                 driver_license=None, location=None,
                 medicare_card=None,
                 country_code='AU'):
        self._raw_result = {}
        self._raw_request = {
            'AcceptTruliooTermsAndConditions': True,
            'ConfigurationName': 'Identity Verification',
            'CleansedAddress': True,
            'DataFields': {},
            'ConsentForDataSources': [],
        }
        self.base_url = 'https://api.globaldatacompany.com'
        # Optional country code
        # 'AU', 'SG', 'CA', 'CN', 'JP', 'NZ', 'ZA', 'GB', 'US'
        self.country = country_code
        self.person = person
        self.driver_license = driver_license
        self.passport = passport
        self.location = location
        self.medicare_card = medicare_card

    @property
    def person(self):
        return self._raw_request['DataFields'].get('PersonInfo', {})

    @person.setter
    def person(self, person):
        data = {}
        if isinstance(person, Person):
            data = {
                "FirstGivenName": person.first_name,
                "FirstSurName": person.last_name,
                'MiddleName': person.middle_name
            }
            if person.date_of_birth:
                data.update({
                    'DayOfBirth': person.date_of_birth.day,
                    'MonthOfBirth': person.date_of_birth.month,
                    'YearOfBirth': person.date_of_birth.year,
                })
            if person.gender is not None:
                data.update({
                    'Gender': person.get_gender_display(),
                })

        self._raw_request['DataFields']['PersonInfo'] = data

    @property
    def country(self):
        return self._raw_request['CountryCode']

    @country.setter
    def country(self, value):
        self._raw_request['CountryCode'] = value

    @property
    def driver_license(self):
        return self._raw_request['DataFields'].get('DriverLicence', {})

    @driver_license.setter
    def driver_license(self, license):
        data = {}
        if isinstance(license, DriverLicense):
            data = {
                'Number': license.number,
                'State': license.state,
            }
            if license.expiry_date:
                data.update({
                    'DayOfExpiry': license.expiry_date.day,
                    'MonthOfExpiry': license.expiry_date.month,
                    'YearOfExpiry': license.expiry_date.year
                })

            if license.card_number:
                self._raw_request['DataFields']['CountrySpecific'] = {
                    'AU': {
                        'RTACardNumber': license.card_number
                    }
                }

        self._raw_request['DataFields']['DriverLicence'] = data



    @property
    def passport(self):
        return self._raw_request['DataFields'].get('Passport', {})

    @passport.setter
    def passport(self, passport):
        data = {}
        if isinstance(passport, Passport):
            data = {
                'Mrz1': passport.mrz1,
                'Mrz2': passport.mrz2,
                'Number': passport.number,
                'DayOfExpiry': passport.expiry_date.day,
                'MonthOfExpiry': passport.expiry_date.month,
                'YearOfExpiry': passport.expiry_date.year
            }
        self._raw_request['DataFields']['Passport'] = data

    @property
    def location(self):
        return self._raw_request['DataFields'].get('Location', {})

    @location.setter
    def location(self, location):
        data = {}
        if isinstance(location, Location):
            data = {
                 # BuildingNumber means Street Number
                'BuildingNumber': location.street_number,
                'StreetName': location.street_name,
                'City': location.city,
                'Suburb': location.suburb,
                'StateProvinceCode': location.state_province_code,
                'Country': location.country.ioc_code,
                'PostalCode': location.postal_code
            }
            # Remove keys that have None value
            data = {k: v for k, v in data.items() if v}

        self._raw_request['DataFields']['Location'] = data

    @property
    def medicare_card(self):
        return self._raw_request['DataFields'].get('CountrySpecific', {}).get('AU', {})

    @medicare_card.setter
    def medicare_card(self, medicare):

        if isinstance(medicare, MedicareCard):
            data = {
                'AU': {
                    "MedicareNumber": medicare.number,
                    "MedicareReference": medicare.reference_number,
                    "MedicareDayOfExpiry": medicare.expiry_date.day,
                    "MedicareMonthOfExpiry": medicare.expiry_date.month,
                    "MedicareYearOfExpiry": medicare.expiry_date.year,
                    "MedicareColor": medicare.colour,
                }
            }
            self._raw_request['DataFields']['CountrySpecific'] = data

    def add_consent(self, consent_name=None):
        if consent_name:
            self._raw_request['ConsentForDataSources'].append(consent_name)

    def add_source_specific_field(self, source_code):
        if source_code == VerificationSource.DVSPASSPORT:
            self._raw_request['DataFields']['CountrySpecific'] = {
                'AU': {
                    'PassportCountry': 'AUS'
                }
            }

    def get_auth_credential(self, is_dvs_request=False):
        if is_dvs_request:
            credential_set = settings.TRULIOO_KEY['DVS']
        else:
            credential_set = settings.TRULIOO_KEY['BACKGROUND']
        return credential_set['USERNAME'], credential_set['PASSWORD'],

    def request_verification(self, source_list):
        for src in source_list:
            self.add_consent(CONSENT_MAP.get(src, None))
            self.add_source_specific_field(src)

        is_dvs_request = len(DVS_SOURCE_SET.intersection(set(source_list))) > 0
        credential_tuple = self.get_auth_credential(is_dvs_request)
        data = requests.post(
            self.base_url + '/verifications/v1/verify/',
            json=self._raw_request,
            auth=credential_tuple)

        return data.json()

    def test_connection(self):
        results = requests.get(self.base_url + '/connection/v1/sayhello/Connection_Succeed')
        return results.json()

    def test_authorization(self):
        results = requests.get(self.base_url + '/connection/v1/testauthentication', auth=self.get_auth_credential())
        return results.content

    def list_country(self):
        return requests.get(
            self.base_url + '/configuration/v1/countrycodes/Identity Verification',
            auth=self.get_auth_credential())
