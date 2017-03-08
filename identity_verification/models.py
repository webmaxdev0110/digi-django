from __future__ import unicode_literals

from datetime import date
from django.contrib.postgres.fields import JSONField
from django.db import models
from django_countries.fields import CountryField

from contacts.models import Person
from core.core_storages import get_document_storage
from core.models import (
    TimeStampedModel,
    YesNoStatusField,
)
from identity_verification.constants import VERIFICATION_SOURCES



class DriverLicense(models.Model):
    person = models.ForeignKey(Person)
    number = models.CharField(max_length=64)
    state = models.CharField(max_length=64, blank=True)
    card_number = models.CharField(max_length=64, blank=True)
    expiry_date = models.DateField(null=True)


class Passport(models.Model):
    person = models.ForeignKey(Person)
    number = models.CharField(max_length=32)
    expiry_date = models.DateField()
    place_of_birth = models.CharField(max_length=128)
    mrz1 = models.CharField(max_length=64, blank=True)
    mrz2 = models.CharField(max_length=64, blank=True)
    country = CountryField()



class PersonVerification(TimeStampedModel, YesNoStatusField):
    person = models.ForeignKey(Person)
    source = models.PositiveSmallIntegerField(choices=VERIFICATION_SOURCES)
    raw_response = JSONField(blank=True, default=dict)
    country = CountryField()


def year_month_day_path(instance, filename):
    today = date.today()
    return 'verification-attachments/{0}/{1}/{2}/{3}'.format(
        today.year, today.month, today.day, filename
    )


class PersonVerificationAttachment(TimeStampedModel):
    file = models.FileField(
        upload_to=year_month_day_path,
        storage=get_document_storage()
    )
    verification = models.ForeignKey(PersonVerification, null=True)