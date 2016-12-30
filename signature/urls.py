from django.conf.urls import url

from signature.views import SignatureView

urlpatterns = [
    url(r'^(?P<style>.+)/(?P<text>.+)$', SignatureView.as_view(), name='draw_signature'),
]
