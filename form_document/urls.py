from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from form_document.rest import (
    FormDocumentRetrieveViewSet,
    FormDocumentCreateUpdateViewSet,
    FormDocumentResponseViewSet,
    SigningVerificationViewSet,
)


api_urlpatterns = [
]

router = DefaultRouter()
router.register(r'form_retrieval', FormDocumentRetrieveViewSet, base_name='form_retrieval')
router.register(r'form', FormDocumentCreateUpdateViewSet)
router.register(r'form_response', FormDocumentResponseViewSet)
router.register(r'signing_verification', SigningVerificationViewSet,
                base_name='signing_verification')

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(api_urlpatterns, namespace='api_form')),
]
