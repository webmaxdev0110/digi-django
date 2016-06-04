from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from accounts.rest import (
    OnboardingCreate,
    AuthenticationAPIView,
)

router = DefaultRouter()
router.register(r'users', OnboardingCreate)


api_urlpatterns = [
    url(r'^auth/login/$',
        AuthenticationAPIView.as_view(),
        name='accounts_auth_login'),

]

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(
        api_urlpatterns,
        namespace='api_accounts'),
        name='api_accounts'),
]
