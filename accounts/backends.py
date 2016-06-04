from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError

from accounts.models import User


class EmailBasedAuthenticationBackend(ModelBackend):
    """
    Supports authentication using email.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        active_users = User.objects.filter(is_active=True)
        try:
            if '@' in username:
                # Try login with email.
                email = username
                user = active_users.get(email__iexact=email)
            else:
                # Try login with username - case-insensitive.
                user = active_users.get(username__iexact=username)
            if user.check_password(password):
                return user
        except User.MultipleObjectsReturned:
            raise ValidationError('Your email address belongs to more than one account')
        except User.DoesNotExist:
            pass

        return None
