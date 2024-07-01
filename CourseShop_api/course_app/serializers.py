from django.db.models import Avg
from rest_framework import serializers
from . import models
from .models import Course, Prerequisite, Enrollment, Review
import subprocess


class ReviewSerializer(serializers.ModelSerializer):
    time_difference = serializers.SerializerMethodField()

    class Meta:
        model = models.Review
        fields = "__all__"

    def get_time_difference(self, obj):
        return obj.time_difference()


class SubtitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subtitle
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = "__all__"


class PrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Prerequisite
        fields = "__all__"


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Season
        fields = ["title"]


class LectureSerializer(serializers.ModelSerializer):
    season_title = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    class Meta:
        model = models.Lecture
        exclude = ["created_at"]

    def get_season_title(self, obj):
        return obj.season.title

    def get_duration(self, obj):
        duration = obj.calculate_duration()
        duration_in_minute = duration / 60
        return round(duration_in_minute, 2)


class CourseSerializer(serializers.ModelSerializer):
    discounted_price_field = serializers.SerializerMethodField()
    is_discounted = serializers.SerializerMethodField()
    prerequisite = serializers.SerializerMethodField()
    seasons = serializers.SerializerMethodField()
    lectures = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    average_review = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    season_numbers = serializers.SerializerMethodField()
    lecture_numbers = serializers.SerializerMethodField()
    total_hours = serializers.SerializerMethodField()

    class Meta:
        model = models.Course
        fields = "__all__"

    def get_discounted_price_field(self, obj):
        return obj.discounted_price()

    def get_is_discounted(self, obj):
        return obj.is_discounted()

    def get_prerequisite(self, obj):
        serializer = PrerequisiteSerializer(obj.course_prerequisite.all(), many=True)
        return serializer.data

    def get_seasons(self, obj):
        serializer = SeasonSerializer(obj.course_seasons.all(), many=True)
        return serializer.data

    def get_lectures(self, obj):
        serializer = LectureSerializer(models.Lecture.objects.filter(season__course=obj), many=True)
        return serializer.data

    def get_comments(self, obj):
        serializer = ReviewSerializer(obj.comments.all(), many=True)
        return serializer.data

    def get_average_review(self, obj):
        review = obj.comments.aggregate(reviews=Avg("rating"))
        avg = 0
        if review['reviews'] is not None:
            avg = float(review['reviews'])
        return avg

    def get_season_numbers(self, obj):
        return obj.course_seasons.count()

    def get_lecture_numbers(self, obj):
        return models.Lecture.objects.filter(season__course=obj).count()

    def get_total_hours(self, obj):
        lectures = models.Lecture.objects.filter(season__course=obj)
        duration = 0
        for lecture in lectures:
            duration += lecture.calculate_duration()
        duration /= 3600
        return round(duration, 2)

    def get_total_reviews(self, obj):
        return obj.comments.all().count()


class EnrollmentSerializer(serializers.ModelSerializer):
    course_slug = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = "__all__"

    def get_course_slug(self, obj):
        return obj.course.slug
