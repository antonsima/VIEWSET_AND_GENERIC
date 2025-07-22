from rest_framework import viewsets

from users.models import Payments
from users.serializers import PaymentsSerializer


class PaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()