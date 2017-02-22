from rest_framework.permissions import AllowAny
from django.contrib.auth import (
    login,
    authenticate,
    logout,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
)
from accounts.models import User
from rest_framework import mixins
from accounts.serializers import (
    PaidSignupFormSerializer,
    UserProfileSerializer,
)


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

class FreeAccountCreate(APIView):

    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        emailSent = False

        user = User.objects.create_user(email, email, password)
        # TODO: set correct permissions
        # TODO: return an error in the response if the email is already registered
        if user:
            emailSent = True
            # TODO: send email

        return Response({
            'emailSent': emailSent
        })

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


class UserAPIView(APIView):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            user = {}
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
