from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        # Creating the user with only email and password fields
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            username=validated_data["email"],  # Use email as the username
            password=validated_data["password"],
        )
        return user