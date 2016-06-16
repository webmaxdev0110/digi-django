from django.conf import settings


def permanent_media_processor(request):
    return {'PERMANENT_MEDIA_URL': settings.PERMANENT_MEDIA_URL}