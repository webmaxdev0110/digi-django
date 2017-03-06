from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from contacts.rest import PersonViewSet

router = DefaultRouter()




router.register(r'person', PersonViewSet, base_name='api_contact_person')


api_urlpatterns = [
]

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(
        api_urlpatterns,
        namespace='api_contacts'),
        name='api_contacts'),
]
