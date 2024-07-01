from django.contrib import admin
from . import models


# Register your models here.

class CartItemInLine(admin.TabularInline):
    model = models.CartItem


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInLine]


class OrderItemInLine(admin.TabularInline):
    model = models.OrderItem


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInLine]


admin.site.register(models.Coupon)
