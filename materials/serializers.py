from rest_framework import serializers

from materials.models import Course, Lesson, Subscription
from materials.validators import VideoURLValidator


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [VideoURLValidator(field="video_url")]


class CourseSerializer(serializers.ModelSerializer):

    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True)
    is_subscribed = serializers.SerializerMethodField()

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False

    class Meta:
        model = Course
        fields = "__all__"


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("user", "course", "created_at")
        read_only_fields = ("user", "created_at")


class CourseWithSubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=obj).exists()
        return False
