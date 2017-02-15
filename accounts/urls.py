from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from accounts.rest import (
    OnboardingCreate,
    AuthenticationAPIView,
    LogoutAPIView,
    UserAPIView,
    SubdomainVerifyAPIView,
)

router = DefaultRouter()
router.register(r'onboarding-create', OnboardingCreate)


api_urlpatterns = [
    url(r'^auth/login/$',
        AuthenticationAPIView.as_view(),
        name='accounts_auth_login'),
    url(r'^auth/logout/$',
        LogoutAPIView.as_view(),
        name='accounts_auth_logout'),
    url(r'^user/$',
        UserAPIView.as_view(),
        name='accounts_user'),
    url(r'^subdomain/verify/$',
        SubdomainVerifyAPIView.as_view(),
        name='subdomain_verify'),
]

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(
        api_urlpatterns,
        namespace='api_accounts'),
        name='api_accounts'),
]
