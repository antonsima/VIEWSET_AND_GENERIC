import django_filters

from users.models import Payments


class PaymentsFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        fields=(('date', 'date')),
        field_labels={'date': 'Дата платежа'}
    )

    class Meta:
        model = Payments
        fields = {
            'course': ['exact'],
            'lesson': ['exact'],
            'payment_method': ['exact'],
        }
