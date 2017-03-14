
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
    site = factory.SubFactory(SiteFactory)

    @factory.post_generation
    def site(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            self.site = extracted
        else:
            if not Site.objects.all().exists():
                site = SiteFactory()
            else:
                site = Site.objects.all()[0]
            self.site = site



class CompanyFactory(factory.DjangoModelFactory):
    class Meta:
        model = Company
    title = factory.sequence(lambda n: 'User <%d>' % n)
    owner = factory.SubFactory(UserFactory)
    active = True
