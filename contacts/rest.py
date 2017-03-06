from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import GenericViewSet
from contacts.models import Person
from contacts.serializers import PersonSeralizer


class PersonViewSet(mixins.RetrieveModelMixin,
                    GenericViewSet):
    serializer_class = PersonSeralizer
    queryset = Person.objects
    authentication_classes = []
    permission_classes = [AllowAny]