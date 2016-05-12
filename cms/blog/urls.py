from django.conf.urls import url

from cms.blog.views import (
    BlogDetailView,
    BlogHomeView,
)

urlpatterns = [
    url(r'^(?P<slug>.*)/$', BlogDetailView.as_view(), name='cms_blog'),
    url(r'^$', BlogHomeView.as_view(), name='cms_blog_home'),
]
