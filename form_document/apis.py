from django.core.urlresolvers import reverse

from form_document.constants import FormSendingMethod
from form_document.models import FormDocumentLink
from form_document.tasks import send_trackable_form_link_email


def list_all_documents_by_user(user):
    # The result should contain all the documents you owned
    # All documents shared with you
    #
    pass


def email_trackable_form_submission_link(form_document, to_email, from_user, first_name):
    link_obj = FormDocumentLink.create_link_for_form(form_document, from_user, method=FormSendingMethod.EMAIL)
    form_tracking_url = reverse('form_tracking_redirect_view', kwargs={
        'form_link_hash': link_obj.hash,
    })
    if from_user.company:
        company_name = from_user.company.title
    else:
        company_name = ''
    send_trackable_form_link_email.delay(
        form_tracking_url,
        to_email,
        form_document.title,
        company_name,
        first_name,
    )
