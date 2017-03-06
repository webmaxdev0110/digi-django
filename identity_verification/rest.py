from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from identity_verification.serializers import IdentityVerificationSerializer


class IdentityVerificationViewSet(ModelViewSet):
    serializer_class = IdentityVerificationSerializer

    def create(self, request, *args, **kwargs):
        super(IdentityVerificationViewSet, self).create(request, *args, **kwargs)

