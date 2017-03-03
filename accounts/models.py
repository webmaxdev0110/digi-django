from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from django.db import models
from timezone_field import TimeZoneField


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
    signup_tag_index = models.CharField(max_length=16, default='', blank=True)
    signup_form_source = models.CharField(max_length=16, default='', blank=True)
    avatar = models.ImageField(blank=True, null=True, upload_to='users/avatars/')
    short_description = models.CharField(blank=True, max_length=256)
    timezone = TimeZoneField(default='Australia/Sydney')


    def has_active_subscription(self):
        return self.plansubscription_set.all().has_active_subscription()

    def is_company_user(self):
        return CompanyMember.objects.filter(user=self).exists()

    def company_user(self):
        if self.is_company_user():
            return CompanyMember.objects.get(user=self)
        else:
            return None


####################################
# Todos:
#   1. Billings
#   2. Permission models
#   3. Feature flags
#   4. Permission specific URLs
####################################


class Company(models.Model):
    """
    Represents a company in our system
    """
    title = models.CharField(max_length=256)

    # company owner would have every permissions
    owner = models.ForeignKey(User, related_name="companies")

    # if company is valid or invalid.
    # when company is registered, it should be reviewed first before it goes public on system.
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class CompanyPermission(models.Model):
    """
    Permission class to manage company's permissions
    Now we only define company's permission scope as "member" and "billing"
    We can add further scope later whenever it comes.

    Using CompanyPermission model, we can define permissions like "management", "employee", for example.

    Notice:
        CompanyPermission class is not for any specific Company object.
        Instead, it would be applied for Company model.
    """

    name = models.CharField(max_length=100, unique=True)

    # member scope permissions
    # notice: edit_member permission covers ability to disable member.
    add_member = models.BooleanField(default=False)
    edit_member = models.BooleanField(default=False)
    delete_member = models.BooleanField(default=False)

    # billing scope permissions
    add_billing = models.BooleanField(default=False)
    edit_billing = models.BooleanField(default=False)
    delete_billing = models.BooleanField(default=False)

    # manage plan permission means up/downgrade company's plan
    manage_plan = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CompanyMember(models.Model):
    """
    Represent company member(i.e team member) in our system
    """
    company = models.OneToOneField(Company, related_name="members")
    user = models.OneToOneField(User)
    permission = models.ForeignKey(CompanyPermission)
    active = models.BooleanField(default=True)


