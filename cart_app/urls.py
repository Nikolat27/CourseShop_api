from . import views
from django.urls import path

urlpatterns = [
    path("cart-detail", views.CartPageView.as_view()),
    path("add-to-cart/<int:pk>", views.CartCreateView.as_view()),
    path("delete-from-cart", views.CartItemDeleteView.as_view()),
    path("checkout", views.CheckoutView.as_view()),
]
