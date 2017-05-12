from django.contrib.sites.models import Site
from rest_framework.generics import get_object_or_404
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
)
from accounts.models import User
from rest_framework import mixins
from accounts.serializers import (
    PaidSignupFormSerializer,
    UserProfileSerializer,
    FreeAccountCreateUserSerializer,
    SimpleUserReadOnlySerializer,
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


class FreeAccountCreate(mixins.CreateModelMixin,
                       GenericViewSet):

    http_method_names = ['post']
    authentication_classes = []
    permission_classes = []
    serializer_class = FreeAccountCreateUserSerializer


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


class UserAPIViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet):
    serializer_class = UserProfileSerializer
    queryset = User.objects

    def get_queryset(self):
        return User.objects.filter(pk=self.request.user.pk)

    def get_object(self):
        obj = get_object_or_404(User.objects, **{'id': self.request.user.pk})

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class SubdomainVerifyAPIView(APIView):

    authentication_classes = []
    permission_classes = []
    # todo: Evaluate security risks

    def post(self, request, format=None):
        subdomain = request.data.get('subdomain', '')
        if len(subdomain) < 4:
            return Response({
                'result': False,
                'error': 'Subdomain must be longer than four characters'
            })

        if Site.objects.filter(domain=subdomain).exists():
            return Response({
                'result': False,
                'error': 'Subdomain already registered'
            })
        else:
            return Response({
                'result': True
            })


class CompanyUserListReadOnlyViewSet(
    mixins.ListModelMixin,
    GenericViewSet):
    serializer_class = SimpleUserReadOnlySerializer

    def get_queryset(self):
        user = self.request.user
        company = user.company
        if not company:
            return User.objects.none()
        return company.user_set.all()