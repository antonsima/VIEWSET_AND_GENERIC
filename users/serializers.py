from rest_framework import serializers

from materials.serializers import CourseSerializer, LessonSerializer
from users.models import Payments, User


class PaymentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payments
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class PaymentsSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)
    payment_method = serializers.CharField(source='get_payment_method_display')
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Payments
        fields = [
            'id',
            'user',
            'date',
            'course',
            'lesson',
            'amount',
            'payment_method',
            'status',
            'stripe_payment_url'
        ]
        read_only_fields = [
            'id',
            'user',
            'date',
            'status',
            'stripe_payment_url'
        ]