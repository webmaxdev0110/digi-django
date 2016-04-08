from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from accounts.rest import OnboardingCreate


router = DefaultRouter()
router.register(r'users', OnboardingCreate)


urlpatterns = [
    url(r'^api/', include(router.urls,
                          namespace='api_accounts'), name='api_accounts'),
]
