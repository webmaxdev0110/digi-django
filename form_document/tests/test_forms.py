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

    def tearDown(self):
        FormDocumentTemplate.objects.all().delete()

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


    def test_retrieve_form_by_slug(self):
        self.template_no_pass.slug = 'test2'
        self.template_no_pass.save()
        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.slug,))
        actual = self.client.get(url, HTTP_HOST=self.template.owner.site.domain)
        self.assertEqual(actual.status_code, 200)
        form_data = actual.json()['form_data']
        self.assertIsNotNone(form_data)

    def test_form_retrieve_will_use_compiled_form(self):
        self.assertEqual(FixedFormDocument.objects.all().count(), 0)
        # Create first copy of Fixedformdocument
        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.slug,))
        result = self.client.get(url, HTTP_HOST=self.template_no_pass.owner.site.domain)
        self.assertEqual(FixedFormDocument.objects.all().count(), 1)
        form = FormDocumentTemplate.objects.get(pk=self.template_no_pass.pk)
        self.assertIsInstance(form.cached_form, FixedFormDocument)

        # Change the form
        self.client.force_login(self.template_no_pass.owner)
        url = reverse('api_form:formdocumenttemplate-detail', args=(self.template_no_pass.pk,))
        actual = self.client.put(url, {
            'title': 'new-title2'
        }, HTTP_HOST=self.template.owner.site.domain)
        form = FormDocumentTemplate.objects.get(pk=self.template_no_pass.pk)

        self.assertIsNone(form.cached_form, None)


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

    def test_modify_template_after_changes_will_create_new_copy(self):

        # Create new document
        user = UserFactory()
        self.client.force_login(user)
        url = reverse('api_form:formdocumenttemplate-list',)
        actual = self.client.post(url, {
            'title': 'new-title'
        }, HTTP_HOST=user.site.domain)
        form_id = actual.json()['id']
        form = FormDocumentTemplate.objects.get(pk=form_id)
        self.assertIn('id', actual.json().keys())

        # Submit answer to this
        answer_response = self.client.post(reverse('api_form:formdocumentresponse-list'), {
            'answers': [{1:{}}],
            'request_action': 'FORM_AUTOSAVE',
            'form_id': form_id
        })
        self.assertIn('response_id', answer_response.json().keys())
        self.assertEqual(FixedFormDocument.objects.count(), 1)

        # Change the form template again
        url = reverse('api_form:formdocumenttemplate-detail', args=(form_id,))

        updated_data = {'form_data': {'empty': True}}
        actual = self.client.put(url, updated_data, format='json', HTTP_HOST=form.owner.site.domain)
        self.assertEqual(actual.status_code, 200)
        # cached_form should be invalidated
        form = FormDocumentTemplate.objects.get(pk=form_id)
        self.assertIsNone(form.cached_form)

        # Assert a history version should not be created,
        # because it is not accessed by a visitor
        self.assertEqual(form.fixedformdocument_set.count(), 1)

        # Submit a new reaponse should create the first copy of the form
        answer_response = self.client.post(reverse('api_form:formdocumentresponse-list'), {
            'answers': [{1: {}}],
            'request_action': 'FORM_AUTOSAVE',
            'form_id': form_id
        })
        self.assertEqual(form.fixedformdocument_set.count(), 2)

    def test_company_member_can_access_form(self):
        pass

    def test_save_duplicated_slug_field(self):

    def test_form_document_partial_update(self):
        site = self.template_no_pass.owner.site
        owner = self.template_no_pass.owner
        self.client.force_login(owner)
        url = reverse('api_form:formdocumenttemplate-detail', args=(self.template_no_pass.pk,))
        updated_data = {'form_data': {'empty': True}}
        actual = self.client.put(url, updated_data, format='json', HTTP_HOST=site.domain)
        self.assertEqual(actual.status_code, 200)
        updated_form_document = FormDocumentTemplate.objects.get(pk=self.template_no_pass.pk)
        self.assertDictContainsSubset(updated_form_document.form_data, {'empty': True})

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