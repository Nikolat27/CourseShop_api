from . import views
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "accounts_app"
urlpatterns = [
    path("register", views.RegisterUser.as_view(), name="user_register"),
    path("login", TokenObtainPairView.as_view(), name="user_login"),
    path("logout", views.UserLogout.as_view(), name="user_logout"),
    path("token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("users", views.UsersList.as_view(), name="user_view"),
]
