from django.conf.urls import url

from testing.views import EmailTestingView

urlpatterns = [
    url(r'^email/(?P<file_name>.+)/(?P<context_json>.+)?$', EmailTestingView.as_view(), name='testing_email'),
]
