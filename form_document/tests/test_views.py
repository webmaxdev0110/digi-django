from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import override_settings

from accounts.factories import UserFactory
from form_document.factories import SimpleFormDocumentTemplateFactory
from form_document.models import FormDocumentLink


class FormDocumentTrackingRedirectTest(TestCase):

    def setUp(self):
        self.template_no_pass = SimpleFormDocumentTemplateFactory.create()

    @override_settings(FRONTEND_PORT=443)
    def test_form_tracking_redirect_url(self):
        link_obj = FormDocumentLink.objects.create(
            form_template=self.template_no_pass,
            hash='test',
            from_user=UserFactory()
        )
        url = reverse('form_tracking_redirect_view', kwargs={
            'form_link_hash': link_obj.hash
        })
        response = self.client.get(url, follow=True)
        url, status_code = response.redirect_chain[-1]
        self.assertEqual(status_code, 302)

        # Assert response is created
        link_obj = FormDocumentLink.objects.get(pk=link_obj.pk)

        self.assertEqual('https://{domain}/forms/{form_id}/{session_id}'.format(**{
            'domain': self.template_no_pass.owner.site.domain,
            'form_id': self.template_no_pass.pk,
            'session_id': link_obj.form_response.pk
        }), url)
