from rest_framework import serializers

from materials.models import Course, Lesson
from materials.validators import VideoURLValidator


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = "__all__"
        validators = [VideoURLValidator(field='video_url')]


class CourseSerializer(serializers.ModelSerializer):

    lesson_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True)

    def get_lesson_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = "__all__"
