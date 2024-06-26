from urllib import parse
from django.db.models import Avg, Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from moviepy.video.io.VideoFileClip import VideoFileClip
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from . import serializers
import requests
from .models import Course, Season, Lecture, Prerequisite, Enrollment, Review, Subtitle, Category
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


# Create your views here.

class CustomResponse(Response):
    def __init__(self, data=None, total_results=None, status=None, template_name=None, headers=None,
                 exception=False, content_type=None, next=None, previous=None, url_path=None):
        data = {"data": data, "total_results": total_results, 'next': next, 'previous': previous,
                'url_path': url_path}
        super().__init__(data=data, status=status, template_name=template_name, headers=headers,
                         exception=exception, content_type=content_type)


class CourseViewSet(ViewSet, PageNumberPagination):
    def list(self, request):
        queryset = Course.objects.all().order_by("-created_at")
        size = request.GET.get("size", 1)
        self.page_size = int(size)
        paginated_queryset = self.paginate_queryset(queryset=queryset, request=request)
        serializer = serializers.CourseSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None):
        course = get_object_or_404(Course, slug=pk)
        serializer = serializers.CourseSerializer(instance=course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = serializers.CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()

        # Create Requirements
        prerequisites_data = request.data.getlist("prerequisite", [])
        prerequisites_list = [Prerequisite(course=course, title=requirement)
                              for requirement in prerequisites_data]
        Prerequisite.objects.bulk_create(prerequisites_list)

        # Create Seasons
        seasons_data = request.data.getlist("seasons", [])
        requirements_list = [Season(course=course, title=season) for season in seasons_data]
        Season.objects.bulk_create(requirements_list)

        return Response({"Course, prerequisites and seasons have been added successfully"},
                        status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        course = get_object_or_404(Course, slug=pk)
        if course:
            course.delete()
            return Response({"response": "Course has been deleted successfully"}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = get_object_or_404(Course, slug=pk)
        serializer = serializers.CourseSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=instance, validated_data=serializer.validated_data)
        return Response({"response": "Your Course has been updated successfully"}, status=status.HTTP_200_OK)


class PrerequisiteDeleteView(APIView):
    def get(self, request, prerequisite_id=None):
        prerequisite = get_object_or_404(Prerequisite, id=prerequisite_id)
        prerequisite.delete()
        return Response({"response": "Your prerequisite has been deleted successfully"})


class LectureCreateView(APIView):
    def post(self, request):
        serializer = serializers.LectureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"response": "Your lecture has been created successfully!"}, status=status.HTTP_201_CREATED)


class LectureUpdateView(APIView):
    def put(self, request, lecture_id):
        lecture = get_object_or_404(Lecture, id=lecture_id)
        print(lecture)
        serializer = serializers.LectureSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance=lecture, validated_data=serializer.validated_data)
        return Response({"response": "Your lecture has been updated successfully!"}, status=status.HTTP_200_OK)


class LectureDeleteView(APIView):
    def delete(self, request, lecture_id):
        lecture = get_object_or_404(Lecture, id=lecture_id)
        lecture.delete()
        return Response({"response": "Your lecture has been deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)


class UserCoursesView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            user_courses = Enrollment.objects.filter(user=request.user)
            if user_courses.exists():
                serializer = serializers.EnrollmentSerializer(instance=user_courses, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"response": "You don`t have any courses"})
        else:
            return Response({"response": "You have to be logged in to see your courses"})


class CheckUserEnrollmentView(APIView):
    def get(self, request, pk=None):
        if request.user.is_authenticated:
            check_user = Enrollment.objects.filter(user=request.user, course_id=pk).exists()
            if check_user:
                return Response({"response": "You have enrolled in this course"})
            else:
                return Response({"response": "You have not enrolled in this course"})


class CreateReviewView(APIView):
    def post(self, request, pk=None):
        if request.user.is_authenticated:
            text = request.data.get("text")
            rating = request.data.get("rating")
            author = request.user
            parent_id = request.data.get("parent_id")
            if not parent_id:
                review = Review.objects.create(course_id=pk, author=author, rating=rating, text=text)
            else:
                review = Review.objects.create(course_id=pk, author=author, rating=rating, text=text,
                                               parent_id=parent_id)

            return Response({"response": "You have created your comment successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({"response": "You have to logged in to create comment"}, status=status.HTTP_400_BAD_REQUEST)


class DeleteReviewView(APIView):
    def delete(self, request, pk):
        if request.user.is_authenticated:
            user = request.user
            review = Review.objects.get(id=pk)
            if user in review.course.instructors.all() or user == review.author:
                review.delete()
                return Response({"response": "You have deleted your review successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"response": "You do not have the permission do delete this comment"},
                                status=status.HTTP_400_BAD_REQUEST)


class SearchCourseView(APIView):
    def get(self, request):
        q = request.data.get("q")
        if q:
            courses = Course.objects.filter(title__icontains=q)
            serializer = serializers.CourseSerializer(instance=courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class SubtitlesView(APIView):
    def get(self, request):
        subtitles = Subtitle.objects.all()
        serializer = serializers.SubtitleSerializer(subtitles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = serializers.CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseFilterView(APIView, PageNumberPagination):
    permission_classes = [AllowAny]

    def get(self, request):
        print("Your request: ", request)
        languages = request.GET.getlist("language")
        subtitles = request.GET.getlist("subtitle")
        categories = request.GET.getlist("category")
        paid = request.GET.get("paid")
        free = request.GET.get("free")
        sort = request.GET.get("sort")
        size = request.GET.get("size", 1)
        self.page_size = int(size)
        min_price = request.GET.get("min_price")
        max_price = request.GET.get("max_price")
        ratings = request.GET.get("ratings")
        url_path = request.get_full_path()
        q = request.GET.get("q")

        courses = Course.objects.all().order_by("-created_at").distinct()

        # Filtering Starts from here
        if q:
            courses = courses.filter(title__icontains=q)

        if categories:
            courses = courses.filter(category__title__in=categories)

        if ratings:
            courses = courses.filter(comments__rating__gte=ratings)

        if languages:
            courses = courses.filter(language__title__in=languages)

        if subtitles:
            courses = courses.filter(subtitles__title__in=subtitles)

        if paid and free:
            courses = courses.filter(costly=True) | courses.filter(costly=False)
        elif paid:
            courses = courses.filter(costly=True)
        elif free:
            courses = courses.filter(costly=False)

        if min_price and max_price:
            courses = courses.filter(price__range=(min_price, max_price))

        if sort == "new":
            courses = courses.order_by("-created_at")
        elif sort == "highest_rated":
            courses = courses.annotate(avg_rating=Avg('comments__rating')).order_by('-avg_rating')
        elif sort == "most_reviewed":
            courses = courses.annotate(total_comments=Count('comments')).order_by('-total_comments')
        elif sort == "discounted":
            courses = courses.filter(is_discounted=True)

        paginated_queryset = self.paginate_queryset(courses, request=request)
        serializer = serializers.CourseSerializer(paginated_queryset, many=True)
        total_results = courses.count()
        return CustomResponse(serializer.data, total_results=total_results, next=self.get_next_link(),
                              previous=self.get_previous_link(), url_path=url_path)


class ClearFilterView(APIView):
    def get(self, request):
        # For clearing the filters we have to these things in order:
        # 1. We need the full url path like this: /course/filter-data?page=1&q=python
        # 2. We need to get the path: '(/course/filter-data)' and the queries:
        # '(?page=1&q=python)' through urlparse module
        url_path = request.GET.get("url_path")
        # url_path value must be the value of 'url_path' variable in CourseFilterView
        # 3. Using parse.urlparse helps us to get the GET parameters of the url_path with 'parsed_url.query'
        parsed_url = parse.urlparse(url_path)

        # query_params is not cleared
        query_params = parse.parse_qs(parsed_url.query)

        # 4. Then we have to keep only the parameters which are needed like page, q and sort
        cleared_queries = {k: v for k, v in query_params.items() if k in ["page", "q", "sort"]}

        # 5. After that we must request to the CourseFilterView class to filter the courses again, So
        # We have to change the cleared_queries which is a dictionary to a query because HTTP GET queries do not
        # accept dictionary, like: {'page': ['1'], 'q': ['python']} = ?page=1&q=python.

        # Reconstruct the URL with filtered query parameters and queries is cleared
        new_query_params = parse.urlencode(cleared_queries, doseq=True)
        new_url = f"/course/filter-data?{new_query_params}"
        return HttpResponseRedirect(new_url)
