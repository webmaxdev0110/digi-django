from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from verifications.rest import EmailVerificationViewSet


router = DefaultRouter()
router.register(r'email', EmailVerificationViewSet, base_name='email')


urlpatterns = [
    url(r'^api/', include(
        router.urls,
        namespace='api_verifications'),
        name='api_verifications'),
]
