from django.conf.urls import url

from docs.views import DocWebAppHome

urlpatterns = [
    url(r'^$', DocWebAppHome.as_view(), name='doc_webapp_home'),
]
