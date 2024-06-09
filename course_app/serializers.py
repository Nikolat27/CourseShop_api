from rest_framework import serializers
from . import models
from .models import Course, Requirements


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Requirements
        fields = "__all__"


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Season
        fields = ["title"]


class LectureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Lecture
        exclude = ["created_at"]


class CourseSerializer(serializers.ModelSerializer):
    requirements = serializers.ListField(child=serializers.CharField(max_length=100))
    discounted_price_field = serializers.SerializerMethodField()
    is_discounted = serializers.SerializerMethodField()
    requirements1 = serializers.SerializerMethodField()
    seasons = serializers.SerializerMethodField()
    lectures = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = "__all__"

    def get_discounted_price_field(self, obj):
        return obj.discounted_price()

    def get_is_discounted(self, obj):
        return obj.is_discounted()

    def get_requirements1(self, obj):
        serializer = RequirementSerializer(obj.course_requirements.all(), many=True)
        return serializer.data

    def get_seasons(self, obj):
        serializer = SeasonSerializer(obj.course_seasons.all(), many=True)
        return serializer.data

    def get_lectures(self, obj):
        serializer = LectureSerializer(models.Lecture.objects.filter(season__course=obj), many=True)
        return serializer.data
