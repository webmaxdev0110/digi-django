from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from billing.models import Plan
from billing.serializers import PlanSerializer


class PlanViewSet(ReadOnlyModelViewSet):
    serializer_class = PlanSerializer
    queryset = Plan.objects
    authentication_classes = []
    permission_classes = [AllowAny]
