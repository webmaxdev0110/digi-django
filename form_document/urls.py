from django.conf.urls import include, url

from rest_framework.routers import DefaultRouter

from form_document.rest import FormDocumentViewSet

api_urlpatterns = [
]

router = DefaultRouter()
#router.register(r'form', FormDocumentViewSet)


api_urlpatterns += router.urls

urlpatterns = [
    url(r'^api/', include(api_urlpatterns,
                          namespace='api_form')),
]
