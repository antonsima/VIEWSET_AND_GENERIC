from rest_framework.routers import DefaultRouter

from users.apps import UsersConfig
from users.views import PaymentsViewSet

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r'payments', PaymentsViewSet, basename='payments')

urlpatterns = [] + router.urls