from rest_framework import serializers
from .models import User


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        if validated_data["password"] == validated_data['password2']:
            user = User.objects.create(username=validated_data['username'], email=validated_data["email"]
                                       , password=validated_data['password'])
            return user
        else:
            raise ValueError("Your first and second password do not match!")
