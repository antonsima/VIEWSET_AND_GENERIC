from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from users.filters import PaymentsFilter
from users.models import Payments
from users.serializers import PaymentsSerializer


class PaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentsFilter