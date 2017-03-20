from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from accounts.rest import (
    OnboardingCreate,
    AuthenticationAPIView,
    FreeAccountCreate,
    LogoutAPIView,
    SubdomainVerifyAPIView,
    UserAPIViewSet,
)
from accounts.views import AccountActivationView

router = DefaultRouter()
router.register(r'onboarding-create', OnboardingCreate)
router.register(r'onboarding-free-plan', FreeAccountCreate, base_name='onboarding-free')


user_detail = UserAPIViewSet.as_view({
    'get': 'retrieve',
    'put': 'update'
})

api_urlpatterns = [
    url(r'^auth/login/$',
        AuthenticationAPIView.as_view(),
        name='accounts_auth_login'),
    url(r'^auth/logout/$',
        LogoutAPIView.as_view(),
        name='accounts_auth_logout'),
    url(r'^user/$',
        user_detail,
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
    url(r'activation/(?P<email>.+)/(?P<activation_code>.+)',
        AccountActivationView.as_view(),
        name='account_email_activation')
]
