"""emondo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include, patterns
from django.contrib import admin
from django.conf import settings

from accounts.views import (
    # LoginView,
    SignupView,
)
from letsencrypt.views import (
    letsencrypt_auth_view_emondo_com_au,
    letsencrypt_auth_view_www_emondo_com_au,
)
from django.contrib.sitemaps.views import sitemap

from notifications.views import telstra_sms_callback_handler
from public.views import HomeView, PublicPricingView
from public_sitemaps.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

handler500 = 'core.errorhandlers.handler500'

urlpatterns = [

    url(r'^$', HomeView.as_view(), name='public_home'),
    url(r'^pricing$', PublicPricingView.as_view(), name='public_pricing'),
    url(r'^docs/', include('docs.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^form_document/', include('form_document.urls')),
    url(r'^notifications/', include('notifications.urls')),
    # Temp URL until Telstra updates their record
    url(r'^notification/sms_callback/telstra/', telstra_sms_callback_handler),
    url(r'^admin/', admin.site.urls),
    url(r'^signature/', include('signature.urls')),
    url(r'^testing/', include('testing.urls')),
    # url(r'^login/$',
    #     LoginView.as_view(),
    #     name='accounts_login'),

    url(r'^signup/$',
        SignupView.as_view(),
        name='accounts_signup'),
    url(r'^blog/', include('cms.blog.urls')),

    # emondo.com.au
    url(r'\.well-known/acme-challenge/TIZhUMHi5Z3bw6xV67n7DXRIAXeKI02pHTnN_ZJm1T4', letsencrypt_auth_view_emondo_com_au),
    # www.emondo.com.au
    url(r'\.well-known/acme-challenge/5iFdtTWY6NcPjDSCan4lKU0MepR3EF0Vu03rTMY-r74', letsencrypt_auth_view_www_emondo_com_au),
    url(r'^verifications/', include('verifications.urls')),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

]
urlpatterns += patterns('',
    url(r'', include('feincms.urls')),
)
if settings.DEBUG:
    urlpatterns += [
        url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
    ]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    ]

admin.site.site_header = 'Emondo'