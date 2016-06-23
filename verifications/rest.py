from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from notifications.vendors.mails.mailgun import Mailgun
from verifications.serializers import EmailAddressVerificationSerializer


class EmailVerificationViewSet(viewsets.ViewSet):
    http_method_names = ['post']
    permission_classes = (AllowAny, )

    @list_route(methods=['post'])
    def verify(self, request):
        email = request.data['email']
        result = Mailgun().validate_email(email)
        serializer = EmailAddressVerificationSerializer({'result': result})
        return Response(serializer.data)
