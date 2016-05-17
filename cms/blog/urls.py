from django.conf.urls import url

from cms.blog.views import (
    BlogDetailView,
    BlogHomeView,
    BlogFeed
)

urlpatterns = [
	url(r'^feed/$', BlogFeed(), name="cms_blog_feed"),
    url(r'^(?P<slug>.*)/$', BlogDetailView.as_view(), name='cms_blog'),
    url(r'^$', BlogHomeView.as_view(), name='cms_blog_home'),
]
