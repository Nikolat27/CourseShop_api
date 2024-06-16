import random
import uuid

from django.shortcuts import get_object_or_404, redirect
from rest_framework.response import Response
from rest_framework.views import APIView

from course_app.models import Course, Enrollment
from . import serializers
from .models import CartItem, Cart, Order, OrderItem, Coupon
from rest_framework import status


# Create your views here.


class CartPageView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
            serializer = serializers.CartSerializer(instance=cart, many=False)
            return Response(serializer.data)
        else:
            session_id = request.session.get("anonymous_user")
            if session_id:
                cart = Cart.objects.filter(session_id=session_id).first()
                serializer = serializers.CartSerializer(instance=cart, many=False)
                return Response(serializer.data)
            else:
                return Response({"response": "Your Cart is empty"})


class CartCreateView(APIView):
    def post(self, request, pk=None):
        course_id = pk
        if request.user.is_authenticated:
            user = request.user
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            session_id = request.session.get("anonymous_user")
            if session_id is None:
                session_id = str(uuid.uuid4())
                request.session['anonymous_user'] = session_id
                request.session.save()
                cart, created = Cart.objects.get_or_create(session_id=session_id)
            else:
                cart, created = Cart.objects.get_or_create(session_id=session_id)
        course = Course.objects.get(id=course_id)
        if not cart.cart_items.filter(course=course).exists():
            CartItem.objects.create(cart=cart, course=course, price=course.discounted_price())
            serializer = serializers.CartSerializer(instance=cart, many=False)
            return Response(serializer.data)
        else:
            return Response({"response": "You have already enrolled in this course!"},
                            status=status.HTTP_400_BAD_REQUEST)


class CartItemDeleteView(APIView):
    def delete(self, request, pk=None):
        cart_item = CartItem.objects.get(id=pk)
        cart_item.delete()
        return Response({"response": "Your Course has been deleted from your cart successfully!"},
                        status=status.HTTP_200_OK)


class ApplyCouponView(APIView):
    def post(self, request):
        coupon_code = request.data.get("coupon_code")
        coupon = get_object_or_404(Coupon, code=coupon_code)
        cart = Cart.objects.get(user=request.user)

        # First we will check that our coupon does exist or not! and is it expired or inactivate or not
        if coupon and not coupon.expired and coupon.active:
            # Second we have to check that our cart`s subtotal is greater than the limit price or not
            if cart.subtotal() > coupon.limit_price and cart.subtotal() < coupon.maximum_price:
                current_usages = Cart.objects.filter(coupon=coupon).count()
                # Third we have to compare the current_usages and max_usages of the coupon
                if current_usages < coupon.max_usage:
                    cart.coupon = coupon
                    cart.coupon_is_used = True
                    cart.save()
                    return Response({"response": "You applied your discount coupon"}, status=status.HTTP_200_OK)


class CheckoutView(APIView):
    # Because I did not have access to a Payment Gateway, I did not implement it
    def get(self, request):
        if request.user.is_authenticated:
            user_cart = Cart.objects.get(user=request.user)
            courses_list = [Enrollment(course=item.course, user=request.user) for item in
                            user_cart.cart_items.all()]
            Enrollment.objects.bulk_create(courses_list)
            user_cart.cart_items.all().delete()

            return Response({"response": "You have purchased your courses successfully! Enjoy them!"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"response": "You have to be logged in to checkout"})
