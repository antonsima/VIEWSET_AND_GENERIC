from django.db import models

from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название курса")
    preview_image = models.ImageField(
        upload_to="course_previews/", verbose_name="Превью курса", blank=True, null=True
    )
    description = models.TextField(verbose_name="Описание курса")

    owner = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название урока")
    description = models.TextField(verbose_name="Описание урока")
    preview_image = models.ImageField(
        upload_to="lesson_previews/", verbose_name="Превью урока", blank=True, null=True
    )
    video_url = models.CharField(
        max_length=150, verbose_name="Ссылка на видео", blank=True, null=True
    )

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="lessons", blank=True, null=True
    )

    owner = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")

    def __str__(self):
        return f"{self.name} - {self.course}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
