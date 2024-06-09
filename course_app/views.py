from django.shortcuts import render, get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from . import serializers
from .models import Course, Requirements


# Create your views here.


class CourseListView(APIView):
    def get(self, request):
        queryset = Course.objects.all()
        serializer = serializers.CourseSerializer(queryset, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CourseDetailView(APIView):
    def get(self, request, pk):
        queryset = get_object_or_404(Course, id=pk)
        serializer = serializers.CourseSerializer(instance=queryset, many=False)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CreateCourseView(APIView):
    def post(self, request):
        serializer = serializers.CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateCourseView(APIView):
    def put(self, request, pk):
        queryset = get_object_or_404(Course, id=pk)
        serializer = serializers.CourseSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(instance=queryset, validated_data=serializer.validated_data)
            return Response({"response": "Course has updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteCourseView(APIView):
    def delete(self, request, pk):
        queryset = get_object_or_404(Course, id=pk)
        if queryset:
            queryset.delete()
            return Response({"response": "Your considered Course has been deleted"},
                            status=status.HTTP_200_OK)


class CourseViewSet(ViewSet):
    def list(self, request):
        queryset = Course.objects.all().order_by("-created_at")
        serializer = serializers.CourseSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        course = get_object_or_404(Course, id=pk)
        serializer = serializers.CourseSerializer(instance=course)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        serializer = serializers.CourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()

        # Create Requirements
        requirements_data = request.data.getlist("requirements", [])
        #
        # requirements_list = [Requirements(course=course, title=requirement)
        #                      for requirement in requirements_data]
        # Requirements.objects.bulk_create(requirements_list)

        print(requirements_data)
        # y = serializers.CourseSerializer(obj)

        return Response({"Course, requirements and seasons have been added successfully"},
                        status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None):
        course = get_object_or_404(Course, id=pk)
        if course:
            course.delete()
            return Response({"response": "Course has been deleted successfully"}, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        instance = get_object_or_404(Course, id=pk)
        serializer = serializers.CourseSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(instance=instance, validated_data=serializer.validated_data)
            return Response({"response": "Your Course has been updated successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_requirement(self, request, course_id=None):
        course = get_object_or_404(Course, id=course_id)
        serializer = serializers.RequirementSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(course=course)
            return Response({"response": "Requirement has been added successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_requirement(self, request, requirement_id=None):
        requirement = get_object_or_404(Requirements, id=requirement_id)
        requirement.delete()
        return Response({"response": "Your requirement has been deleted successfully"}, status=status.HTTP_200_OK)


class RequirementCreateView(APIView):
    def post(self, request, course_id=None):
        course = get_object_or_404(Course, id=course_id)
        serializer = serializers.RequirementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course=course)
            return Response({"response": "Requirement has been added successfully"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequirementDeleteView(APIView):
    def get(self, request, requirement_id=None):
        requirement = get_object_or_404(Requirements, id=requirement_id)
        requirement.delete()
        return Response({"response": "Your requirement has been deleted successfully"})
