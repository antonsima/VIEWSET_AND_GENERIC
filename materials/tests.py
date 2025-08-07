from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription
from materials.paginators import LessonPaginator
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        # Создаем группы пользователей
        self.moder_group = Group.objects.create(name="moders")

        # Создаем пользователей через сериализатор или напрямую с email
        self.regular_user = User.objects.create(
            email="regular@user.com",
            password="testpass123",
            is_active=True,
            first_name="Regular",
            last_name="User",
        )

        self.moder_user = User.objects.create(
            email="moder@user.com",
            password="testpass123",
            is_active=True,
            first_name="Moder",
            last_name="User",
        )
        self.moder_user.groups.add(self.moder_group)  # Исправлено groups вместо groups

        self.owner_user = User.objects.create(
            email="owner@user.com",
            password="testpass123",
            is_active=True,
            first_name="Owner",
            last_name="User",
        )

        # Создаем тестовые курсы
        self.course1 = Course.objects.create(
            name="Course 1", description="Description 1", owner=self.owner_user
        )
        self.course2 = Course.objects.create(
            name="Course 2", description="Description 2", owner=self.owner_user
        )

        # Создаем тестовые уроки
        self.lesson1 = Lesson.objects.create(
            name="Lesson 1",
            description="Description 1",
            course=self.course1,
            owner=self.owner_user,
        )
        self.lesson2 = Lesson.objects.create(
            name="Lesson 2",
            description="Description 2",
            course=self.course1,
            owner=self.owner_user,
        )

    def test_create_lesson_authenticated(self):
        """Тест создания урока авторизованным пользователем"""
        self.client.force_authenticate(user=self.regular_user)

        data = {
            "name": "New Lesson",
            "description": "New Description",
            "video_url": "https://www.youtube.com/new",
            "course": self.course1.id,
        }

        response = self.client.post(reverse("materials:lesson-create"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            response.json(),
            {
                "id": 3,
                "name": "New Lesson",
                "description": "New Description",
                "preview_image": None,
                "video_url": "https://www.youtube.com/new",
                "course": self.course1.id,
                "owner": self.regular_user.id,
            },
        )

    def test_create_lesson_unauthenticated(self):
        """Тест создания урока неавторизованным пользователем"""
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "video_url": "https://www.youtube.com/new",
            "course": self.course1.id,
        }

        response = self.client.post(reverse("materials:lesson-create"), data=data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_moderator(self):
        """Тест создания урока модератором (должен быть запрещен)"""
        self.client.force_authenticate(user=self.moder_user)

        data = {
            "name": "New Lesson",
            "description": "New Description",
            "video_url": "https://www.youtube.com/new",
            "course": self.course2.id,
        }

        response = self.client.post(reverse("materials:lesson-create"), data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_lessons(self):
        """Тест получения списка уроков"""
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(reverse("materials:lesson-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(response.json()["results"]), 2)

    def test_retrieve_lesson_owner(self):
        """Тест просмотра урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.get(
            reverse("materials:lesson-get", args=[self.lesson1.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json()["name"], self.lesson1.name)

    def test_retrieve_lesson_moderator(self):
        """Тест просмотра урока модератором"""
        self.client.force_authenticate(user=self.moder_user)

        response = self.client.get(
            reverse("materials:lesson-get", args=[self.lesson1.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_lesson_unauthorized(self):
        """Тест просмотра урока неавторизованным пользователем"""
        response = self.client.get(
            reverse("materials:lesson-get", args=[self.lesson1.id])
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_lesson_owner(self):
        """Тест обновления урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)

        data = {
            "name": "Updated Lesson",
            "description": "Updated Description",
            "video_url": "https://www.youtube.com/updated",
            "course": self.course1.id,
        }

        response = self.client.put(
            reverse("materials:lesson-update", args=[self.lesson1.id]), data=data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, "Updated Lesson")

    def test_update_lesson_moderator(self):
        """Тест обновления урока модератором"""
        self.client.force_authenticate(user=self.moder_user)

        data = {
            "name": "Updated Lesson by Moderator",
            "description": "Updated Description by Moderator",
            "video_url": "https://www.youtube.com/updated_by_moderator",
            "course": self.course1.id,
        }

        response = self.client.put(
            reverse("materials:lesson-update", args=[self.lesson1.id]), data=data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, "Updated Lesson by Moderator")

    def test_update_lesson_unauthorized(self):
        """Тест обновления урока неавторизованным пользователем"""
        data = {
            "name": "Updated Lesson",
            "description": "Updated Description",
            "video_url": "https://www.youtube.com/updated",
            "course": self.course1.id,
        }

        response = self.client.put(
            reverse("materials:lesson-update", args=[self.lesson1.id]), data=data
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_lesson_owner(self):
        """Тест удаления урока владельцем"""
        self.client.force_authenticate(user=self.owner_user)

        response = self.client.delete(
            reverse("materials:lesson-delete", args=[self.lesson1.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Lesson.objects.filter(id=self.lesson1.id).exists())

    def test_delete_lesson_moderator(self):
        """Тест удаления урока модератором (должен быть запрещен)"""
        self.client.force_authenticate(user=self.moder_user)

        response = self.client.delete(
            reverse("materials:lesson-delete", args=[self.lesson1.id])
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_unauthorized(self):
        """Тест удаления урока неавторизованным пользователем"""
        response = self.client.delete(
            reverse("materials:lesson-delete", args=[self.lesson1.id])
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pagination(self):
        """Тест пагинации списка уроков"""
        self.client.force_authenticate(user=self.regular_user)

        # Создаем дополнительные уроки для теста пагинации
        Lesson.objects.bulk_create(
            [
                Lesson(
                    name=f"Lesson {i}",
                    description=f"Description {i}",
                    video_url=f"https://www.youtube.com/lesson{i}",
                    course=self.course2,
                    owner=self.regular_user,
                )
                for i in range(3, 13)  # Создаем 10 уроков, всего будет 12
            ]
        )

        response = self.client.get(reverse("materials:lesson-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что количество элементов на странице соответствует настройкам пагинатора
        self.assertEqual(len(response.json()["results"]), LessonPaginator.page_size)

        # Проверяем наличие ключа 'next' в ответе (должна быть вторая страница)
        self.assertIn("next", response.json())


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        # Создаем группы пользователей
        self.moder_group = Group.objects.create(name="moders")

        # Создаем пользователей
        self.regular_user = User.objects.create(
            username="regular_user", password="testpass123", is_active=True
        )

        self.moder_user = User.objects.create(
            username="moder_user", password="testpass123", is_active=True
        )
        self.moder_user.groups.add(self.moder_group)

        self.owner_user = User.objects.create(
            username="owner_user", password="testpass123", is_active=True
        )

        # Создаем тестовые курсы
        self.course1 = Course.objects.create(
            name="Course 1", description="Description 1", owner=self.owner_user
        )
        self.course2 = Course.objects.create(
            name="Course 2", description="Description 2", owner=self.owner_user
        )

        # Создаем тестовые уроки
        self.lesson1 = Lesson.objects.create(
            name="Lesson 1",
            description="Description 1",
            course=self.course1,
            owner=self.owner_user,
        )
        self.lesson2 = Lesson.objects.create(
            name="Lesson 2",
            description="Description 2",
            course=self.course1,
            owner=self.owner_user,
        )

    # Тесты для создания урока
    def test_create_lesson_by_regular_user(self):
        """Проверка создания урока обычным пользователем"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("materials:lesson-create")
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "course": self.course1.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)
        self.assertEqual(Lesson.objects.last().owner, self.regular_user)

    def test_create_lesson_by_moderator(self):
        """Проверка что модератор не может создать урок"""
        self.client.force_authenticate(user=self.moder_user)
        url = reverse("materials:lesson-create")
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "course": self.course1.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_unauthorized(self):
        """Проверка что неавторизованный пользователь не может создать урок"""
        url = reverse("materials:lesson-create")
        data = {
            "name": "New Lesson",
            "description": "New Description",
            "course": self.course1.id,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Lesson.objects.count(), 2)

    # Тесты для просмотра списка уроков
    def test_list_lessons(self):
        """Проверка получения списка уроков"""
        url = reverse("materials:lesson-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    # Тесты для просмотра деталей урока
    def test_retrieve_lesson_by_owner(self):
        """Проверка что владелец может просматривать урок"""
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("materials:lesson-get", args=[self.lesson1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Lesson 1")

    def test_retrieve_lesson_by_moderator(self):
        """Проверка что модератор может просматривать урок"""
        self.client.force_authenticate(user=self.moder_user)
        url = reverse("materials:lesson-get", args=[self.lesson1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Lesson 1")

    def test_retrieve_lesson_by_unauthorized(self):
        """Проверка что неавторизованный пользователь не может просматривать урок"""
        url = reverse("materials:lesson-get", args=[self.lesson1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Тесты для обновления урока
    def test_update_lesson_by_owner(self):
        """Проверка что владелец может обновлять урок"""
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("materials:lesson-update", args=[self.lesson1.id])
        data = {"name": "Updated Lesson"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, "Updated Lesson")

    def test_update_lesson_by_moderator(self):
        """Проверка что модератор может обновлять урок"""
        self.client.force_authenticate(user=self.moder_user)
        url = reverse("materials:lesson-update", args=[self.lesson1.id])
        data = {"name": "Updated Lesson"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, "Updated Lesson")

    def test_update_lesson_by_regular_user(self):
        """Проверка что обычный пользователь не может обновлять урок"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("materials:lesson-update", args=[self.lesson1.id])
        data = {"name": "Updated Lesson"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, "Lesson 1")

    # Тесты для удаления урока
    def test_delete_lesson_by_owner(self):
        """Проверка что владелец может удалять урок"""
        self.client.force_authenticate(user=self.owner_user)
        url = reverse("materials:lesson-delete", args=[self.lesson1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_delete_lesson_by_moderator(self):
        """Проверка что модератор не может удалять урок"""
        self.client.force_authenticate(user=self.moder_user)
        url = reverse("materials:lesson-delete", args=[self.lesson1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_delete_lesson_by_regular_user(self):
        """Проверка что обычный пользователь не может удалять урок"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("materials:lesson-delete", args=[self.lesson1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        # Создаем пользователей с email вместо username
        self.user1 = User.objects.create(
            email="user1@example.com",
            password="testpass123",
            is_active=True,
            first_name="User1",
            last_name="Test",
        )
        self.user2 = User.objects.create(
            email="user2@example.com",
            password="testpass123",
            is_active=True,
            first_name="User2",
            last_name="Test",
        )

        # Создаем тестовые курсы
        self.course1 = Course.objects.create(
            name="Course 1", description="Description 1", owner=self.user1
        )
        self.course2 = Course.objects.create(
            name="Course 2", description="Description 2", owner=self.user1
        )

        # Создаем тестовые подписки
        self.subscription1 = Subscription.objects.create(
            user=self.user1, course=self.course1
        )

    def test_add_subscription(self):
        """Проверка добавления подписки"""
        self.client.force_authenticate(user=self.user2)
        url = reverse("materials:subscriptions")
        data = {"course_id": self.course1.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user2, course=self.course1).exists()
        )

    def test_remove_subscription(self):
        """Проверка удаления подписки"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("materials:subscriptions")
        data = {"course_id": self.course1.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user1, course=self.course1).exists()
        )

    def test_subscription_unauthorized(self):
        """Проверка что неавторизованный пользователь не может управлять подписками"""
        url = reverse("materials:subscriptions")
        data = {"course_id": self.course1.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_invalid_course(self):
        """Проверка обработки несуществующего курса"""
        self.client.force_authenticate(user=self.user1)
        url = reverse("materials:subscriptions")
        data = {"course_id": 999}  # Несуществующий ID
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
