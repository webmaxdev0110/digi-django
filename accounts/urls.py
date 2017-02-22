from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from accounts.rest import (
    OnboardingCreate,
    AuthenticationAPIView,
    LogoutAPIView,
    UserAPIViewSet,
)

router = DefaultRouter()
router.register(r'onboarding-create', OnboardingCreate)


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
]

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(
        api_urlpatterns,
        namespace='api_accounts'),
        name='api_accounts'),
]
