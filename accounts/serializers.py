from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "role", "is_verified"]

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "phone_number", "password", "confirm_password", "role"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)  # Hashes the password automatically
        user.is_active = False  # Set the user as inactive until OTP is verified
        user.generate_otp()  # Generate OTP for the user
        return user

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(request=self.context.get("request"), email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_verified:
            raise serializers.ValidationError("Account not verified.")
        if not user.is_active:
            raise serializers.ValidationError("Account is inactive. Please verify your OTP.")

        tokens = RefreshToken.for_user(user)
        return {
            "access": str(tokens.access_token),
            "refresh": str(tokens),
            "role": user.role
        }

class GoogleLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()