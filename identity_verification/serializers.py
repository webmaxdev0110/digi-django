from datetime import datetime

from django_countries.fields import Country
from rest_framework import serializers
from contacts.models import Person
from contacts.serializers import PersonSerializer
from core.models import YesNoStatusChoice
from identity_verification.constants import VerificationSource
from identity_verification.models import (
    PersonVerification,
    Passport,
    PersonVerificationAttachment,
)
from identity_verification.trulioo import TruliooRequestBuilder
from identity_verification.utils import is_passport_match


class PassportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = (
            'person',
            'number',
            'expiry_date',
            'place_of_birth',
            'country',
        )



class IdentityVerificationSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField()
    verification_data = serializers.JSONField(required=False)
    person = serializers.JSONField()
    attachment_ids = serializers.ListField(required=False)

    class Meta:
        model = PersonVerification
        fields = (
            'type',
            'verification_data',
            'person',
            'attachment_ids'
        )

    def create(self, validated_data):
        submitted_person = validated_data['person']
        if submitted_person.get('id', None):
            person = Person.objects.get(pk=submitted_person['id'])
        else:
            person = PersonSerializer(data=submitted_person)
            person.is_valid()
            person = person.save()

        verification_type = validated_data['type']
        person_verification = PersonVerification.objects.create(
            person=person, source=verification_type, country=Country(code='AU')
        )

        if validated_data['type'] == VerificationSource.MANUAL_FILE_UPLOAD:
            # todo: handle file save, save it to PersonVerificationAttachment model
            person_verification.status = YesNoStatusChoice.PASSED
            for attachment_id in validated_data['attachment_ids']:
                pa = PersonVerificationAttachment.objects.get(pk=attachment_id)
                pa.verification=person_verification
                pa.save()

        if validated_data['type'] == VerificationSource.DVSPASSPORT:
            submitted_passport = validated_data['verification_data']['passport']
            # todo: Refactor this into serializer
            passport = Passport(
                person=person,
                number=submitted_passport['number'],
                expiry_date=datetime.strptime(submitted_passport['expiry_date'], '%Y-%m-%d'),
                place_of_birth=submitted_passport['place_of_birth'],
                country=Country(code=submitted_passport['country'])
            )
            passport.save()

            request_builder = TruliooRequestBuilder()
            request_builder.passport = passport
            request_builder.person = person

            raw_response = request_builder.request_verification([VerificationSource.DVSPASSPORT])
            if is_passport_match(raw_response):
                person_verification.status = YesNoStatusChoice.PASSED
            else:
                person_verification.status = YesNoStatusChoice.REJECTED
            person_verification.raw_response = raw_response
        person_verification.save()

        return person_verification


class PersonVerificationAttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonVerificationAttachment
        fields = (
            'id',
            'file',
            'verification',
        )
        extra_kwargs = {
            'file': {'write_only': True},
            'verification': {'write_only': True}
        }
