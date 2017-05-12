from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import override_settings
from rest_framework.test import (
    APITestCase,
)
from accounts.factories import UserFactory
from contacts.models import Person
from form_document.constants import FormCompletionStatus
from form_document.factories import (
    SimpleFormDocumentTemplateFactory,
    ApplicationFormDocumentTemplateFactory,
)
from form_document.models import (
    FixedFormDocument,
    FormDocumentTemplate,
    FormDocumentResponse,
    FormDocumentResponseAttachment,
)
import random
from django.core import mail
import mock


class FormDocumentRestAPITestCase(APITestCase):

    def setUp(self):
        self.template_no_pass = SimpleFormDocumentTemplateFactory.create()
        self.template = SimpleFormDocumentTemplateFactory.create(access_code='1234')

    def tearDown(self):
        FormDocumentTemplate.objects.all().delete()

    def test_anonymous_user_can_not_list_forms(self):
        url = reverse('api_form:formdocumenttemplate-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_list_form_document_templates(self):
        url = reverse('api_form:formdocumenttemplate-list')
        owner = self.template.owner
        self.client.force_login(owner)
        response = self.client.get(url)
        response_json = response.json()
        self.assertItemsEqual(['count', 'data', 'next', 'previous'], response_json.keys())
        first_data_obj = response_json['data'][0]
        expected_keys = ['id', 'slug', 'title', 'created', 'created_by', 'status']
        self.assertItemsEqual(expected_keys, first_data_obj.keys())

        # Test order by id
        url = reverse('api_form:formdocumenttemplate-list')
        response = self.client.get(url, data={
            'ordering': 'id'
        })
        response_json = response.json()
        self.assertGreater(response_json['data'][1]['id'], response_json['data'][0]['id'])

    def test_list_form_should_not_contain_archived_objects(self):
        FormDocumentTemplate.objects.archive()
        url = reverse('api_form:formdocumenttemplate-list')
        owner = self.template.owner
        self.client.force_login(owner)
        response = self.client.get(url)
        response_json = response.json()
        self.assertEqual(len(response_json['data']), 0)

    def test_archive_a_form(self):
        template_id = self.template.pk
        url = reverse('api_form:formdocumenttemplate-archive', args=(self.template.pk,))
        owner = self.template.owner
        self.client.force_login(owner)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        template = FormDocumentTemplate.objects.get(pk=template_id)
        self.assertIsNotNone(template.archived_on)

    def test_duplicate_a_form(self):
        url = reverse('api_form:formdocumenttemplate-duplicate', args=(self.template.pk,))
        owner = self.template.owner
        self.client.force_login(owner)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 201)
        new_form_document_template_id = response.json()['id']
        new_template = FormDocumentTemplate.objects.get(pk=new_form_document_template_id)
        self.assertEqual(self.template.form_data, new_template.form_data)
        self.assertEqual(self.template.form_config, new_template.form_config)
        self.assertIsNotNone(new_template.uploaded_document)

    def test_anonymous_user_can_retrieve_form(self):
        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.pk,))
        site = self.template.owner.site
        actual = self.client.get(url, HTTP_ORIGIN=site.domain)
        self.assertEqual(actual.status_code, 200)
        form_data = actual.json()['form_data']
        self.assertIsNotNone(form_data)
        excepted_keys = [
            u'assets_urls',
            u'title',
            u'number_of_pages',
            u'slug',
            u'form_config',
            u'form_data',
            u'document_mapping',
            u'id'
        ]

        self.assertListEqual(excepted_keys, actual.json().keys())

    def test_access_code_protected_form(self):
        # Test Anonymous access needs access_code
        url = reverse('api_form:form_retrieval-detail', args=(self.template.pk,))
        actual = self.client.get(url, HTTP_ORIGIN=self.template.owner.site.domain)
        form_data = actual.json()['form_data']
        self.assertIsNone(form_data)

        # Test with access code, form_data is returned
        actual = self.client.get(url, data={
            'access_code': self.template.access_code
        }, HTTP_ORIGIN='example.com')
        self.assertIsNotNone(actual.json()['form_data'])

    def test_form_owner_can_access_form(self):
        # Form owner needs no access_code
        url = reverse('api_form:form_retrieval-detail', args=(self.template.pk,))
        owner = self.template.owner
        self.client.force_login(owner)
        actual = self.client.get(url, HTTP_ORIGIN=self.template.owner.site.domain)
        self.assertIsNone(actual.json()['form_data'])


    def test_retrieve_form_by_slug(self):
        self.template_no_pass.slug = 'test2'
        self.template_no_pass.save()
        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.slug,))
        actual = self.client.get(url, HTTP_ORIGIN=self.template.owner.site.domain)
        self.assertEqual(actual.status_code, 200)
        form_data = actual.json()['form_data']
        self.assertIsNotNone(form_data)

    def test_form_retrieve_will_use_compiled_form(self):
        self.assertEqual(FixedFormDocument.objects.all().count(), 0)
        # Create first copy of Fixedformdocument
        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.slug,))
        result = self.client.get(url, HTTP_ORIGIN=self.template_no_pass.owner.site.domain)
        self.assertEqual(FixedFormDocument.objects.all().count(), 1)
        form = FormDocumentTemplate.objects.get(pk=self.template_no_pass.pk)
        self.assertIsInstance(form.cached_form, FixedFormDocument)

        # Change the form
        self.client.force_login(self.template_no_pass.owner)
        url = reverse('api_form:formdocumenttemplate-detail', args=(self.template_no_pass.pk,))
        actual = self.client.put(url, {
            'title': 'new-title2'
        }, HTTP_ORIGIN=self.template.owner.site.domain)
        form = FormDocumentTemplate.objects.get(pk=self.template_no_pass.pk)

        self.assertIsNone(form.cached_form, None)

        # Retrieve the form again should return the new title
        form.get_or_create_compiled_form()
        form.cached_form.title = 'Changed'
        form.cached_form.save()
        cached_form = FixedFormDocument.objects.get(pk=form.cached_form.pk)
        self.assertEqual(cached_form.title, 'Changed')

        url = reverse('api_form:form_retrieval-detail', args=(self.template_no_pass.slug,))
        result = self.client.get(url, HTTP_ORIGIN=self.template_no_pass.owner.site.domain)
        self.assertEqual(result.json()['title'], 'Changed')


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
        }, HTTP_ORIGIN=user.site.domain)
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

        updated_data = {'form_data': {'questions': [{'type': 'QuestionType'}]}}
        actual = self.client.put(url, updated_data, format='json', HTTP_ORIGIN=form.owner.site.domain)
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

    def test_admin_modify_form_answer_rest_api(self):
        pass

    def test_admin_edit_form_answer_api(self):
        site = self.template_no_pass.owner.site
        owner = self.template_no_pass.owner
        self.client.force_login(owner)
        # Submit answer to this
        answer_response = self.client.post(reverse('api_form:formdocumentresponse-list'), {
            'answers': [{'id': 1, 'value': 'old'}],
            'request_action': 'FORM_AUTOSAVE',
            'form_id': self.template_no_pass.pk
        }, HTTP_ORIGIN=self.template_no_pass.owner.site.domain, format='json')
        form_response_id = answer_response.json()['response_id']

        # Now change answer id 1
        self.client.post(reverse('api_form:formdocumentresponse-change-answer', args=(form_response_id,)), {
            'question_number': 1,
            'value': 'new_value',
        })
        # Now change an answer that has no value
        self.client.post(reverse('api_form:formdocumentresponse-change-answer', args=(form_response_id,)), {
            'question_number': 2,
            'value': 'new_value2',
        })

        updated_response = FormDocumentResponse.objects.get(pk=form_response_id)
        self.assertEqual(updated_response.answers[1]['value'], 'new_value2')


    def test_form_document_partial_update(self):
        site = self.template_no_pass.owner.site
        owner = self.template_no_pass.owner
        self.client.force_login(owner)
        url = reverse('api_form:formdocumenttemplate-detail', args=(self.template_no_pass.pk,))
        updated_data = {'form_data': {'empty': True}}
        actual = self.client.put(url, updated_data, format='json', HTTP_ORIGIN=site.domain)
        self.assertEqual(actual.status_code, 200)
        updated_form_document = FormDocumentTemplate.objects.get(pk=self.template_no_pass.pk)
        self.assertDictContainsSubset(updated_form_document.form_data, {'empty': True})

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @mock.patch("form_document.tasks.send_trackable_form_link_email.delay")
    def test_email_trackable_form_link(self, send):
        owner = self.template_no_pass.owner
        self.client.force_login(owner)
        url = reverse(
            'api_form:formdocumenttemplate-email-form-tracking-link',
            args=(self.template_no_pass.pk,))
        response = self.client.post(url, {
            'email': 'test@example.com'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        send.assert_called_once()


class FormResponseRestAPITestCase(APITestCase):

    def setUp(self):
        self.template_no_pass = SimpleFormDocumentTemplateFactory.create()

    def test_anonymous_user_can_submit_form(self):
        answer_response = self.client.post(reverse('api_form:formdocumentresponse-list'), {
            'answers': [{1: {}}],
            'request_action': 'FORM_AUTOSAVE',
            'form_id': self.template_no_pass.pk
        }, HTTP_ORIGIN=self.template_no_pass.owner.site.domain, format='json')
        self.assertIn('response_id', answer_response.json().keys())
        # Test that response has cached_form attribute and form_document
        response_id = answer_response.json()['response_id']
        response = FormDocumentResponse.objects.get(pk=response_id)
        self.assertIsNotNone(response.cached_form)
        self.assertIsNotNone(response.form_document)

    def test_anonymouse_user_can_update_form_reponse_object(self):
        attachment = SimpleUploadedFile(
            "file_attachment.pdf",
            "file_content", content_type="application/pdf")
        upload_url = reverse('api_form:formdocumentresponse-upload-attachment')

        cached_form = self.template_no_pass.compile_form()
        empty_response = cached_form.create_empty_response()
        answer_response = self.client.post(upload_url, {
            'file': attachment,
            'response_id': empty_response.pk
        }, HTTP_ORIGIN=self.template_no_pass.owner.site.domain, format='multipart')
        self.assertEqual(FixedFormDocument.objects.count(), 1)
        # Should create the response object
        self.assertEqual(FormDocumentResponse.objects.count(), 1)
        response_obj = FormDocumentResponse.objects.all()[0]

        self.assertEqual(FormDocumentResponseAttachment.objects.count(), 1)
        attachment_id = answer_response.json()['attachment_id']
        attachment = FormDocumentResponseAttachment.objects.get(pk=attachment_id)
        # Should save the file
        # file should linked back to the response object
        self.assertEqual(attachment.response.pk, response_obj.pk)

    def test_upload_file_for_file_field_no_response_object(self):
        attachment = SimpleUploadedFile(
            "file_attachment.pdf",
            "file_content", content_type="application/pdf")
        upload_url = reverse('api_form:formdocumentresponse-upload-attachment')
        answer_response = self.client.post(upload_url, {
            'file': attachment,
            'form_id': self.template_no_pass.pk
        }, HTTP_ORIGIN=self.template_no_pass.owner.site.domain, format='multipart')
        self.assertEqual(FixedFormDocument.objects.count(), 1)
        # Should create the response object
        self.assertEqual(FormDocumentResponse.objects.count(), 1)
        response_obj = FormDocumentResponse.objects.all()[0]

        self.assertEqual(FormDocumentResponseAttachment.objects.count(), 1)
        attachment_id = answer_response.json()['attachment_id']
        attachment = FormDocumentResponseAttachment.objects.get(pk=attachment_id)
        # Should save the file
        # file should linked back to the response object
        self.assertEqual(attachment.response.pk, response_obj.pk)
        self.assertIn('file_name', answer_response.json().keys())

    def test_upload_file_for_file_field_validations(self):
        # Max length of filename is 100
        attachment = SimpleUploadedFile(
            "%s.pdf" % 'filename' * 100,
            "file_content", content_type="application/pdf")
        upload_url = reverse('api_form:formdocumentresponse-upload-attachment')
        answer_response = self.client.post(upload_url, {
            'file': attachment,
            'form_id': self.template_no_pass.pk
        }, HTTP_ORIGIN=self.template_no_pass.owner.site.domain, format='multipart')
        excepted = {
            'file': [u'File name exceeds 100 characters']
        }
        self.assertDictContainsSubset(excepted, answer_response.json())

    def test_upload_file_response(self):
        # Max length of filename is 100
        file_name = 'filename_unique%s.pdf' % random.randint(0, 1000)
        attachment = SimpleUploadedFile(
            file_name,
            "file_content", content_type="application/pdf")
        upload_url = reverse('api_form:formdocumentresponse-upload-attachment')
        answer_response = self.client.post(upload_url, {
            'file': attachment,
            'form_id': self.template_no_pass.pk
        }, HTTP_ORIGIN=self.template_no_pass.owner.site.domain, format='multipart')

        self.assertEqual(FormDocumentResponseAttachment.objects.count(), 1)
        attachment_id = answer_response.json()['attachment_id']
        attachment = FormDocumentResponseAttachment.objects.get(pk=attachment_id)

        excepted = {
            'attachment_id': attachment_id,
            'file_name': file_name
        }
        self.assertDictContainsSubset(excepted, answer_response.json())


    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_sending_form_resume_link(self):
        mail.outbox = []
        url = reverse('api_form:formdocumentresponse-send-resume-link')
        cached_form = self.template_no_pass.compile_form()
        empty_response = cached_form.create_empty_response()
        test_email = 'test@example.com'
        answer_response = self.client.post(url, {
            'response_id': empty_response.pk,
            'email': test_email,
            'form_continue_url': 'http://{0}/form_continue/url'.format(self.template_no_pass.owner.site.domain),
        }, HTTP_ORIGIN=self.template_no_pass.owner.site.domain, format='json')
        self.assertEqual(answer_response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)

    def test_form_submission_can_be_seen_by_form_owner(self):
        pass

    def test_form_submission_can_be_seen_by_company_member(self):
        pass

    def test_form_submission_cannot_seen_by_external_company_user(self):
        pass

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_sending_signing_person_verification_email(self):
        mail.outbox = []
        url = reverse('api_form:signing_verification-request-email-verification-code')
        cached_form = self.template_no_pass.compile_form()
        empty_response = cached_form.create_empty_response()
        test_email = 'test@example.com'
        test_name = 'John Smith'
        answer_response = self.client.post(url, {
            'response_id': empty_response.pk,
            'email': test_email,
            'display_name': test_name,
        }, format='json')

        self.assertEqual(answer_response.status_code, 200)
        # Verification email should be sent
        self.assertEqual(len(mail.outbox), 1)

        # New person should be created
        persons = Person.objects.filter(email=test_email)
        self.assertEqual(persons.count(), 1)
        self.assertEqual(persons[0].display_name, test_name)

        # Email should contain the verification code
        verification_code = persons[0].email_verification_code
        self.assertTrue(verification_code in mail.outbox[0].body)
        self.assertFalse(persons[0].is_email_verified)

        verification_url = reverse('api_form:signing_verification-verify-email-code')

        verification_response = self.client.post(verification_url, {
            'response_id': empty_response.pk,
            'email': test_email,
            'code': verification_code
        }, format='json')
        self.assertEqual(verification_response.status_code, 200)
        self.assertTrue(Person.objects.get(pk=persons[0].pk).is_email_verified)
        signing_retrieval_url = reverse('api_form:signing_verification-check-email')

        email_check_response = self.client.get(signing_retrieval_url, {
            'response_id': empty_response.pk,
            'email': test_email,
        }, format='json')

        expected = {
            'is_verified': True
        }

        self.assertDictContainsSubset(expected, email_check_response.json())

    def test_form_response_detail_api(self):
        template = ApplicationFormDocumentTemplateFactory.create()
        cached_form = template.compile_form()
        response = cached_form.create_empty_response()
        response.answers = [{
            'id': 1,
            'value': 'John'
        }]
        response.save()
        detail_url = reverse('api_form:formdocumentresponse-detail', args=(response.pk,))
        attachment = SimpleUploadedFile(
            "file_attachment.pdf",
            "file_content", content_type="application/pdf")

        response_attachment = FormDocumentResponseAttachment(
            attachment=attachment,
            response=response
        )
        response_attachment.save()
        form_response_detail = self.client.get(detail_url)
        response_json = form_response_detail.json()

        # Test completion percent
        self.assertAlmostEqual(0.1, response_json['completion_percent'])
        
        # Test contact_name
        # Test contact_phone
        # Test contact_email
        # Test attachments
        attachments = response_json['attachments']
        self.assertEqual(1, len(attachments))
        attachment = attachments[0]
        keys = attachment.keys()
        self.assertIn('file_name', keys)
        self.assertIn('file_size', keys)
        self.assertIn('file_url', keys)

    def test_form_response_in_multiple_status(self):
        self.client.force_login(self.template_no_pass.owner)

        response_list_url = reverse('api_form:formdocumentresponse-list')
        # submission 1 with status 1
        response1 = self.template_no_pass.compile_form().create_empty_response()
        response1.status = FormCompletionStatus.SAVED
        response1.save()
        # submission 1 with status 2
        response2 = self.template_no_pass.compile_form().create_empty_response()
        response2.status = FormCompletionStatus.SUBMITTED
        response2.save()

        saved_response = self.client.get(response_list_url, data={
            'status': FormCompletionStatus.SAVED
        }, format='json')
        self.assertEqual(saved_response.json()['count'], 1)
        self.assertEqual(saved_response.json()['data'][0]['status'], 'Saved')


        saved_submitted_resopnse = self.client.get(response_list_url, data={
            'status': ','.join([str(FormCompletionStatus.SAVED), str(FormCompletionStatus.SUBMITTED)])
        }, format='json')
        self.assertEqual(saved_submitted_resopnse.json()['count'], 2)

    def test_assign_submission(self):
        self.client.force_login(self.template_no_pass.owner)

        response = self.client.get(reverse('api_form:formdocumentresponse-list'), {
            'assignee__id': self.template_no_pass.owner.pk
        })
        self.assertEqual(response.json()['count'], 0)

        # Create an response and assign to owner
        form_response = self.template_no_pass.compile_form().create_empty_response()

        response = self.client.post(reverse('api_form:formdocumentresponse-assign', args=(form_response.pk,)), {
            'user_id': self.template_no_pass.owner.pk
        })
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('api_form:formdocumentresponse-list'), {
            'assignee__id': self.template_no_pass.owner.pk
        })
        self.assertEqual(response.json()['count'], 1)
