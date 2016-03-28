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

from letsencrypt.views import letsencrypt_auth_view
from public.views import HomeView

urlpatterns = [

    url(r'^$', HomeView.as_view(), name='public_home'),
    url(r'^docs/', include('docs.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'\.well-known/acme-challenge/DyfZfS79fi5pyJ7je61krPjbVmAOsM6-eSpf8mSczmY', letsencrypt_auth_view)

]
