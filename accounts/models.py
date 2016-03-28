from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.db import models


class User(AbstractUser):
    """
    Users within the Django authentication system are represented by this
    model.

    Username, password and email are required. Other fields are optional.
    """

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    country = CountryField(default='AU', blank=True)
    last_active = models.DateTimeField(null=True, blank=True)
    is_pre_launch_signup = models.BooleanField(default=False)

