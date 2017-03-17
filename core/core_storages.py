import os
import ntpath
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto import S3BotoStorage


class MediaStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = 'emondo-media'
        super(MediaStorage, self).__init__(*args, **kwargs)


class ProtectedDocumentStorage(S3BotoStorage):
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = 'emondo-documents'
        kwargs['default_acl'] = 'private'
        kwargs['bucket_acl'] = 'private'
        kwargs['querystring_auth'] = True
        kwargs['querystring_expire'] = 1800
        kwargs['file_overwrite'] = False
        super(ProtectedDocumentStorage, self).__init__(*args, **kwargs)


get_document_storage = lambda: ProtectedDocumentStorage() if settings.UPLOAD_DOC_TO_S3 else FileSystemStorage()


def owner_document_path(prefix, user_pk):
    return '{0}/users/{1}/'.format(
        prefix,
        user_pk,
    )
