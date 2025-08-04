from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import PaymentsViewSet, UserCreateAPIView, CreatePaymentView, PaymentStatusView

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", PaymentsViewSet, basename="payments")

urlpatterns = [
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
    path('payments/create/', CreatePaymentView.as_view(), name='create-payment'),
    path('payments/<int:payment_id>/status/', PaymentStatusView.as_view(), name='payment-status'),
] + router.urls
