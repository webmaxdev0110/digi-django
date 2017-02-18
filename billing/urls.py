from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from billing.rest import PlanViewSet

router = DefaultRouter()
router.register(r'plan', PlanViewSet)


api_urlpatterns = [
]

api_urlpatterns += router.urls


urlpatterns = [
    url(r'^api/', include(
        api_urlpatterns,
        namespace='api_billing'),
        name='api_billing'),
]
