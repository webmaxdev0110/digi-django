from __future__ import unicode_literals

from django.db import models

# Create your models here.
from core.models import TimeStampedModel

NOTIFICATION_CHOICES = (
    ('0', 'SMS',),
     ('1', 'EMAIL',),
)


class NotificationTransaction(TimeStampedModel, models.Model):
    type = models.CharField(choices=NOTIFICATION_CHOICES, max_length=1)
