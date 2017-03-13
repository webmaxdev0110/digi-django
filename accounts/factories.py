
import factory
from django.core.files.base import ContentFile

from accounts.models import User
# from form_document.models import FormDocument


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.sequence(lambda n: 'User <%d>' % n)
    is_active = True
