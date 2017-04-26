from django.test import TestCase
from django.test import override_settings
from django.core import mail
from form_document.apis import email_trackable_form_submission_link
from form_document.factories import SimpleFormDocumentTemplateFactory


class FormDocumentAPITestCase(TestCase):

    def setUp(self):
        self.template_no_pass = SimpleFormDocumentTemplateFactory.create()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_sending_trackable_form_link(self):
        mail.outbox = []
        user = self.template_no_pass.owner
        email_trackable_form_submission_link(
            self.template_no_pass,
            'text@example.com',
            user
        )
        self.assertEqual(len(mail.outbox), 1)

