from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from accounts.rest import (
    OnboardingCreate,
    AuthenticationAPIView,
    FreeAccountCreate,
    LogoutAPIView,
    UserAPIView,
)

router = DefaultRouter()
router.register(r'onboarding-create', OnboardingCreate)
router.register(r'onboarding-free-plan', FreeAccountCreate, base_name='onboarding-free')


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

]

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(
        api_urlpatterns,
        namespace='api_accounts'),
        name='api_accounts'),
]
