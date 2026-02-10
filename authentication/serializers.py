from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.conf import settings

from .models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.get_or_create(
            user=user,
            defaults={
                "image_url": getattr(settings, "DEFAULT_PROFILE_IMAGE_URL", "")
            },
        )
        return user
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email")

    class Meta:
        model = Profile
        fields = ("username", "email", "image_url", "image_public_id")

    def validate_email(self, value):
        user = self.context["request"].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        email = user_data.get("email")
        if email is not None:
            instance.user.email = email
            instance.user.save(update_fields=["email"])

        if "image_url" in validated_data:
            instance.image_url = validated_data["image_url"]
        if "image_public_id" in validated_data:
            instance.image_public_id = validated_data["image_public_id"]

        instance.save()
        return instance