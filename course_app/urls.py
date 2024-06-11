from . import views
from django.urls import path

urlpatterns = [
    path("delete_prerequisite/<int:requirement_id>", views.PrerequisiteDeleteView.as_view()),
    path("create_lecture", views.LectureCreateView.as_view()),
    path("update_lecture/<int:lecture_id>", views.LectureUpdateView.as_view()),
    path("delete_lecture/<int:lecture_id>", views.LectureDeleteView.as_view()),
    path("user_courses", views.UserCoursesView.as_view()),
    path("check_user_enrollment", views.CheckUserEnrollmentView.as_view()),
    path("create_review/<int:pk>", views.CreateReviewView.as_view()),
    path("delete_review/<int:pk>", views.DeleteReviewView.as_view()),
]
