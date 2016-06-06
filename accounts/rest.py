from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import login, authenticate, logout
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from accounts.models import User
from rest_framework import mixins
from accounts.serializers import PaidSignupFormSerializer


class OnboardingCreate(mixins.CreateModelMixin,
                       GenericViewSet):

    serializer_class = PaidSignupFormSerializer
    permission_classes = (AllowAny,)
    queryset = User.objects

    def create(self, request, *args, **kwargs):
        response = super(OnboardingCreate, self).create(
            request, *args, **kwargs)
        # send email

        return response

    def perform_create(self, serializer):
        super(OnboardingCreate, self).perform_create(serializer)


class AuthenticationAPIView(APIView):

    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []

    # Login request
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        authenticated = False

        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            authenticated = True

        return Response({
            'authenticated': authenticated
        })


class LogoutAPIView(APIView):
    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        logout(request)

        return Response({
            'authenticated': False
        })
