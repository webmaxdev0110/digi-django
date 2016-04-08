from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from rest_framework.viewsets import GenericViewSet
from accounts.models import User
from rest_framework import mixins
from accounts.serializers import OnboardingSignupFormSerializer


class OnboardingCreate(mixins.CreateModelMixin,
                       GenericViewSet):

    serializer_class = OnboardingSignupFormSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects

    def create(self, request, *args, **kwargs):
        response = super(OnboardingCreate, self).create(
            request, *args, **kwargs)
        # send email

        return response

    def perform_create(self, serializer):
        super(OnboardingCreate, self).perform_create(serializer)
