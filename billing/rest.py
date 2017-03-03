from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import (
    ReadOnlyModelViewSet,
    GenericViewSet,
)

from billing.models import Plan
from billing.serializers import (
    PlanSerializer,
    SubscriptionSerializer,
)


class PlanViewSet(ReadOnlyModelViewSet):
    serializer_class = PlanSerializer
    queryset = Plan.objects
    authentication_classes = []
    permission_classes = [AllowAny]


class SubscriptionViewSet(mixins.CreateModelMixin,
                   GenericViewSet):

    serializer_class = SubscriptionSerializer
    permission_classes = []


