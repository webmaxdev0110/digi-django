from django.utils.translation import ugettext_lazy as _


class FormSendingMethod(object):
    DIRECT = 0
    EMAIL = 1
    SMS = 2

FORM_SENDING_METHOD_CHOICES = (
    (FormSendingMethod.DIRECT, _('Direct')),
    (FormSendingMethod.EMAIL, _('Email')),
    (FormSendingMethod.SMS, _('SMS')),
)
