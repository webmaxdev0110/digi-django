from __future__ import unicode_literals

from django.db import models

# Create your models here.
from core.models import TimeStampedModel



class SMSNotificationTransaction(TimeStampedModel, models.Model):
    remote_id = models.CharField(max_length=128, null=True)
    user_response = models.CharField(max_length=256, null=True)
    message = models.CharField(max_length=512)
    dest_number = models.CharField(max_length=64)
    status = models.CharField(max_length=16, null=True)


