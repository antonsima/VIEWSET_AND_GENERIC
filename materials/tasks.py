import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from materials.models import Subscription
from users.models import User

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_notification(course_id):
    subscriptions = Subscription.objects.filter(course_id=course_id).select_related(
        "user", "course"
    )

    for subscription in subscriptions:
        subject = f"Обновление курса {subscription.course.title}"
        message = f'Курс "{subscription.course.title}", на который вы подписаны, был обновлен.'
        recipient_list = [subscription.user.email]

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=recipient_list,
            fail_silently=False,
        )


@shared_task
def deactivate_inactive_users():
    """
    Задача для деактивации пользователей, которые не заходили более месяца
    """
    try:
        inactive_threshold = timezone.now() - timedelta(days=30)

        inactive_users = User.objects.filter(
            last_login__lt=inactive_threshold, is_active=True
        )

        count = inactive_users.update(is_active=False)

        logger.info(f"Деактивировано {count} неактивных пользователей")
        return f"Успешно деактивировано {count} пользователей"

    except Exception as e:
        logger.error(f"Ошибка при деактивации неактивных пользователей: {str(e)}")
        raise
