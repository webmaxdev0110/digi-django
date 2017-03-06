from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.models import YesNoStatusChoice
from identity_verification.models import PersonVerification
from identity_verification.serializers import IdentityVerificationSerializer


class IdentityVerificationViewSet(mixins.CreateModelMixin, GenericViewSet):
    serializer_class = IdentityVerificationSerializer
    queryset = PersonVerification.objects
    authentication_classes = []
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inst = serializer.save()

        return Response({'result': inst.status == YesNoStatusChoice.PASSED})


