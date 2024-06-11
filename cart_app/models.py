from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from accounts_app.models import User
from course_app.models import Course


# Create your models here.


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_cart", null=True, blank=True)
    session_id = models.CharField(max_length=100, null=True, blank=True, unique=True)

    def __str__(self):
        if self.user:
            return self.user.username

    def len(self):
        len = 0
        for item in self.cart_items.all():
            len += 1
        return len

    def subtotal(self):
        subtotal = 0
        for item in self.cart_items.all():
            subtotal += item.price
        return subtotal


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_in_cart")
    price = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f"{self.cart} - {self.course.title}"


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    limit_price = models.DecimalField(max_digits=10, decimal_places=3)
    maximum_price = models.DecimalField(max_digits=10, decimal_places=3)
    max_usage = models.PositiveSmallIntegerField(default=1)
    valid_from = models.DateTimeField(auto_now=False)
    valid_to = models.DateTimeField(auto_now=False)
    active = models.BooleanField(default=True)
    expired = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return f"{self.code} - {self.discount_percentage} - Active: {self.active}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        now = timezone.now()
        if self.valid_from and self.valid_to:
            if now > self.valid_to:
                self.expired = True
                self.save()
            else:
                self.save()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_orders")
    subtotal = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    coupon_used = models.BooleanField(default=False, null=True, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="coupon_used", null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    order_code = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return f"{self.user.username} - {self.subtotal} - {self.is_paid} - {self.order_code}"

    def calculate_subtotal(self):
        subtotal = 0
        for item in self.order_items.all():
            item.price += subtotal

        if not self.coupon_used:
            self.subtotal = subtotal
        else:
            discounted_price = (self.coupon.discount_percentage / 100) * subtotal
            subtotal = self.subtotal - discounted_price
            self.subtotal = subtotal
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="order_items")
    price = models.DecimalField(max_digits=10, decimal_places=3)

    def __str__(self):
        return f"{self.course.title} - {self.price}"
