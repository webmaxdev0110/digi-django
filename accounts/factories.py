
import factory
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile

from accounts.models import (
    User,
    Company,
)


class SiteFactory(factory.DjangoModelFactory):
    class Meta:
        model = Site
    name = 'example'
    domain = 'example.com'


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.sequence(lambda n: 'User <%d>' % n)
    is_active = True
class CompanyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Company
    title = factory.sequence(lambda n: 'User <%d>' % n)
    owner = factory.SubFactory(UserFactory)
    active = True
