from bson import ObjectId
from django.core.files.base import ContentFile
from gridfs import GridFS
from pymongo import MongoClient
from emails.apis import (
    get_email_rendering_base_context,
    render_html_email,
    render_text_email,
)
from datetime import datetime
from emondo.celery import app
from form_document.models import FormDocumentResponse
from notifications.tasks import send_one_off_email
from django.conf import settings
from celery import chain
import subprocess
import ntpath



@app.task
def send_trackable_form_link_email(form_tracking_url, to_address, form_title, company_name='', first_name=None):
    subject = 'My online form has arrived from %s' % company_name
    context = get_email_rendering_base_context()
    context.update({
        'form_tracking_url': form_tracking_url,
        'subject': subject,
        'form_title': form_title,
        'first_name': first_name,
        'company_name': company_name
    })
    html_email = render_html_email('form_link_invitation', context)
    text_email = render_text_email('form_link_invitation', context)
    send_one_off_email.delay(subject, [to_address], text_email, html_email)


@app.task
def store_pdf_fill_task(response_id):
    # Store all files in mongodb
    submission = FormDocumentResponse.objects.get(pk=response_id)
    cached_form = submission.cached_form
    client = MongoClient(settings.MONGO_HOST, 27017)
    db = client.emondo
    pdf_job_db = db.pdf_job

    form_template_document = cached_form.template.uploaded_document
    grid_fs = GridFS(db, collection="fs")
    file_id = grid_fs.put(form_template_document.read(), filename=ntpath.basename(form_template_document.name))

    inserted_result = pdf_job_db.insert_one({
        'form_response_id': submission.pk,
        'answers': submission.answers,
        'document_mapping': cached_form.document_mapping,
        'form_data': cached_form.form_data,
        'completed': False,
        'created': datetime.now(),
        'last_modified': None,
        'input_file_id': str(file_id),
        'output_file_id': ''
    })
    return str(inserted_result.inserted_id)


@app.task
def populate_pdf_document(job_id):
    subprocess.call([
        'java', '-jar', 'path_to_jar.jar',
        'populate_pdf_document',
        '--job-id', job_id])


@app.task
def upload_populated_pdf_to_storage(form_response_id, mongo_file_id):
    form_response = FormDocumentResponse.objects.get(pk=form_response_id)
    client = MongoClient(settings.MONGO_HOST, 27017)
    db = client.emondo
    pdf_file = grid_fs.find_one({'_id': ObjectId(mongo_file_id)})
    grid_fs = GridFS(db, collection="fs")
    form_response.populated_document.save(pdf_file.filename, ContentFile(pdf_file.read()))


@app.task
def request_populating_pdf_document(response_id):
    chain(
        store_pdf_fill_task.s(response_id),
        populate_pdf_document.s(),
        upload_populated_pdf_to_storage.s()
    )()
