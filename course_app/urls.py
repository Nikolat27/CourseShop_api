from . import views
from django.urls import path

urlpatterns = [
    path("courses", views.CourseListView.as_view()),
    path("course_detail/<int:pk>", views.CourseDetailView.as_view()),
    path("course_detail/<int:pk>", views.CourseDetailView.as_view()),
    path("create_requirement/<int:course_id>", views.RequirementCreateView.as_view()),
    path("delete_requirement/<int:requirement_id>", views.RequirementDeleteView.as_view()),
]
