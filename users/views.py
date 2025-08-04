from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from materials.models import Course, Lesson
from users.filters import PaymentsFilter
from users.models import Payments, User
from users.serializers import PaymentsSerializer, UserSerializer
from users.services import create_stripe_product, create_stripe_price, create_stripe_checkout_session, \
    retrieve_stripe_session
from viewset_and_generic import settings


class PaymentsViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentsSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = PaymentsFilter


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class CreatePaymentView(APIView):

    def post(self, request):
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')

        if not course_id and not lesson_id:
            return Response(
                {"error": "Необходимо указать course_id или lesson_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if course_id:
                item = Course.objects.get(id=course_id)
                amount = item.price
                name = item.name
                description = item.description
            else:
                item = Lesson.objects.get(id=lesson_id)
                amount = item.price
                name = item.name
                description = item.course.name if item.course else "Урок"
        except (Course.DoesNotExist, Lesson.DoesNotExist):
            return Response(
                {"error": "Курс или урок не найдены"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Создаем запись о платеже
        payment = Payments.objects.create(
            user=request.user,
            course=item if isinstance(item, Course) else None,
            lesson=item if isinstance(item, Lesson) else None,
            amount=amount,
            payment_method='stripe'
        )

        try:
            # Создаем продукт в Stripe
            product = create_stripe_product(name, description)
            price = create_stripe_price(product.id, amount)

            success_url = f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{settings.FRONTEND_URL}/payment/cancel?session_id={{CHECKOUT_SESSION_ID}}"

            session = create_stripe_checkout_session(price.id, success_url, cancel_url)

            # Обновляем платеж с данными из Stripe
            payment.stripe_product_id = product.id
            payment.stripe_price_id = price.id
            payment.stripe_session_id = session.id
            payment.stripe_payment_url = session.url
            payment.save()

            serializer = PaymentsSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            payment.status = 'failed'
            payment.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentStatusView(APIView):

    def get(self, request, payment_id):
        try:
            payment = Payments.objects.get(id=payment_id, user=request.user)
            serializer = PaymentsSerializer(payment)
            return Response(serializer.data)
        except Payments.DoesNotExist:
            return Response(
                {"error": "Платеж не найден"},
                status=status.HTTP_404_NOT_FOUND
            )