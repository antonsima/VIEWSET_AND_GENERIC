from django.contrib.auth.models import AbstractUser
from django.db import models

from materials.models import Course, Lesson
from viewset_and_generic import settings


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("cash", "Наличные"),
        ("card", "Банковская карта"),
        ("transfer", "Перевод"),
        ("stripe", "Stripe"),
    )

    STATUS_CHOICES = (
        ("pending", "Ожидает оплаты"),
        ("paid", "Оплачено"),
        ("canceled", "Отменено"),
        ("failed", "Ошибка оплаты"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    date = models.DateTimeField(auto_now_add=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    amount = models.PositiveIntegerField(verbose_name="Сумма платежа")
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHODS, default="card"
    )
    session_id = models.CharField(max_length=100, blank=True, null=True)
    link = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Платеж {self.id} - {self.amount} рублей ({self.get_status_display()})"

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-date"]
