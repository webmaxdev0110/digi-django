from django_countries.fields import Country
from rest_framework import serializers
from contacts.models import Person
from contacts.serializers import PersonSerializer
from identity_verification.constants import VerificationSource
from identity_verification.models import PersonVerification, Passport
from identity_verification.trulioo import TruliooRequestBuilder


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = (
            'person'
            'number',
            'expiry_date',
            'place_of_birth',
            'country'
        )


class IdentityVerificationSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField()
    verification_data = serializers.JSONField()
    person = PersonSerializer

    class Meta:
        model = PersonVerification
        fields = (
            'type',
            'verification_data',
            'person',
        )

    def create(self, validated_data):
        submitted_person = validated_data['person']
        person = PersonSerializer(**submitted_person)
        person = person.save()

        verification_data = validated_data['verification_data']
        verification_type = validated_data['type']
        person_verification = PersonVerification.objects.create(
            person=person, source=verification_type, country=Country(code='AU')
        )

        if validated_data['type'] == VerificationSource.MANUAL_FILE_UPLOAD:
            # todo: handle file save, save it to PersonVerificationAttachment model
            pass


        if validated_data['type'] == VerificationSource.DVSPASSPORT:
            passport = PassportSerializer(**verification_data['pasport'])
            passport.person = person
            passport.save()

            request_builder = TruliooRequestBuilder()
            request_builder.passport = passport
            result = request_builder.request_verification([VerificationSource.DVSPASSPORT])
            # todo: test whether the result is success or not and update the PersonVerification object

            person_verification.raw_response = result

