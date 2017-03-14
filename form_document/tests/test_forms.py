from django.core.urlresolvers import reverse
from rest_framework.test import (
    APITestCase,
)
from accounts.factories import UserFactory
from core.constants import StatusChoices
from form_document.factories import FormDocumentTemplateFactory
from form_document.models import FixedFormDocument, FormDocumentTemplate


class FormDocumentRestAPITestCase(APITestCase):

    def setUp(self):
        self.template_no_pass = FormDocumentTemplateFactory.create()
        self.template = FormDocumentTemplateFactory.create(access_code='1234')

    def test_anonymous_user_can_retrieve_form(self):
        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.pk,))
        site = self.template.owner.site
        actual = self.client.get(url, HTTP_HOST=site.domain)
        self.assertEqual(actual.status_code, 200)
        form_data = actual.json()['form_data']
        self.assertIsNotNone(form_data)

    def test_access_code_protected_form(self):
        # Test Anonymous access needs access_code
        url = reverse('api_form:form_retrieval-detail', args=(self.template.pk,))
        actual = self.client.get(url, HTTP_HOST=self.template.owner.site.domain)
        form_data = actual.json()['form_data']
        self.assertIsNone(form_data)

        # Test with access code, form_data is returned
        actual = self.client.get(url, data={
            'access_code': self.template.access_code
        }, HTTP_HOST='example.com')
        self.assertIsNotNone(actual.json()['form_data'])

    def test_form_owner_can_access_form(self):
        # Form owner needs no access_code
        url = reverse('api_form:form_retrieval-detail', args=(self.template.pk,))
        owner = self.template.owner
        self.client.force_login(owner)
        actual = self.client.get(url, HTTP_HOST=self.template.owner.site.domain)
        self.assertIsNone(actual.json()['form_data'])

    def test_update_form_should_create_compiled_form(self):
        self.client.force_login(self.template_no_pass.owner)
        url = reverse('api_form:formdocumenttemplate-detail', args=(self.template_no_pass.pk,))

        actual = self.client.put(url, {
            'title': 'new-title'
        }, HTTP_HOST=self.template.owner.site.domain)
        self.assertDictContainsSubset(actual.json(), {'id': self.template_no_pass.pk})
        self.assertEqual(FixedFormDocument.objects.count(), 0)

        self.template_no_pass.status = StatusChoices.LIVE
        self.template_no_pass.save()

        actual = self.client.put(url, {
            'title': 'new-title2'
        }, HTTP_HOST=self.template.owner.site.domain)
        self.assertEqual(FixedFormDocument.objects.count(), 1)

    def test_retrieve_form_by_slug(self):
        self.template_no_pass.slug = 'test2'
        self.template_no_pass.save()
        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.slug,))
        actual = self.client.get(url, HTTP_HOST=self.template.owner.site.domain)
        self.assertEqual(actual.status_code, 200)
        form_data = actual.json()['form_data']
        self.assertIsNotNone(form_data)

    def test_form_create_should_have_correct_owner(self):
        user = UserFactory()
        self.client.force_login(user)
        url = reverse('api_form:formdocumenttemplate-list')

        actual = self.client.post(url, {
            'title': 'my-form-title',
            'slug': 'slug',
            'form_data': {},
        }, format='json')

        self.assertIn('id', actual.json().keys())
        form_id = actual.json()['id']
        form = FormDocumentTemplate.objects.get(pk=form_id)
        self.assertEqual(form.owner.pk, user.pk)

    def test_save_owner_cannot_have_duplicated_form_urls(self):
        user = UserFactory()
        self.client.force_login(user)
        url = reverse('api_form:formdocumenttemplate-list')

        actual = self.client.post(url, {
            'title': 'my-form-title',
            'slug': 'slug',
            'form_data': {},
        }, format='json')
        self.assertEqual(actual.status_code, 201)
        self.assertIn('id', actual.json().keys())

        actual = self.client.post(url, {
            'title': 'my-form-title',
            'slug': 'slug',
            'form_data': {},
        }, format='json')
        self.assertEqual(actual.status_code, 400)
        self.assertIn('slug', actual.json().keys())

    def test_form_creation_should_give_company_wide_access(self):
        pass

    def test_company_member_can_access_form(self):
        pass

    def test_save_duplicated_slug_field(self):
        pass


class FormResponseRestAPITestCase(APITestCase):

    def test_anonymous_user_can_submit_form(self):
        pass

    def test_form_submission_can_be_seen_by_form_owner(self):
        pass

    def test_form_submission_can_be_seen_by_company_member(self):
        pass

    def test_form_submission_cannot_seen_by_external_company_user(self):
        pass