
import factory
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile

from accounts.models import User
# from form_document.models import FormDocument


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
