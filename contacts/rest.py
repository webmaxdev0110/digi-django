from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from contacts.models import Person
from contacts.serializers import PersonSerializer


class PersonViewSet(mixins.RetrieveModelMixin,
                    GenericViewSet):
    serializer_class = PersonSerializer
    queryset = Person.objects
    authentication_classes = []
    permission_classes = [AllowAny]