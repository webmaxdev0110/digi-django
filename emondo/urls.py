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
from django.conf.urls import url, include
from django.contrib import admin

from letsencrypt.views import (
    letsencrypt_auth_view_emondo_com_au,
    letsencrypt_auth_view_www_emondo_com_au,
)
from public.views import HomeView

urlpatterns = [

    url(r'^$', HomeView.as_view(), name='public_home'),
    url(r'^docs/', include('docs.urls')),
    url(r'^admin/', admin.site.urls),
    # emondo.com.au
    url(r'\.well-known/acme-challenge/TIZhUMHi5Z3bw6xV67n7DXRIAXeKI02pHTnN_ZJm1T4', letsencrypt_auth_view_emondo_com_au),
    # www.emondo.com.au
    url(r'\.well-known/acme-challenge/5iFdtTWY6NcPjDSCan4lKU0MepR3EF0Vu03rTMY-r74', letsencrypt_auth_view_www_emondo_com_au),

]
