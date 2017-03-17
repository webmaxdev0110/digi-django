from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from form_document.rest import (
    FormDocumentRetrieveViewSet,
    FormDocumentCreateUpdateViewSet,
    FormDocumentResponseViewSet,
)


api_urlpatterns = [
]

router = DefaultRouter()
router.register(r'form_retrieval', FormDocumentRetrieveViewSet, base_name='form_retrieval')
router.register(r'form', FormDocumentCreateUpdateViewSet)
router.register(r'form_response', FormDocumentResponseViewSet)

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(api_urlpatterns, namespace='api_form')),
]
