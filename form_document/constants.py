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

class FormCompletionStatus(object):
    UNOPENED = 1
    OPENED = 2
    SAVED = 3
    SUBMITTED = 4
    ABANDONED = 5
    AUTO_SAVED = 6

FORM_COMPLETION_STATUS = (
    (FormCompletionStatus.UNOPENED, _('Unopen')),
    (FormCompletionStatus.ABANDONED, _('Abandoned')),
    (FormCompletionStatus.OPENED, _('Opened')),
    (FormCompletionStatus.SAVED, _('Saved')),
    (FormCompletionStatus.SUBMITTED, _('Submitted')),
    (FormCompletionStatus.AUTO_SAVED, _('Auto Saved')),
)