from rest_framework import serializers
from . import models


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = models.Cart
        fields = "__all__"

    def get_cart_items(self, obj):
        serializer = CartItemSerializer(obj.cart_items.all(), many=True)
        return serializer.data
