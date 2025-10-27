from rest_framework import status
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, OTPVerifySerializer, LoginSerializer, GoogleLoginSerializer
from .models import User
from django.core.mail import send_mail
from rest_framework_simplejwt.exceptions import TokenError
from django.core.mail import send_mail
from django.conf import settings


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = False  # Set the user as inactive until OTP is verified
        user.generate_otp()  # Generate OTP for the user
        user.save()

        send_mail(
            "Your OTP Code",
            f"Your OTP is {user.otp}",
            "agronepalss@gmail.com",  # Sender email
            [user.email],
            fail_silently=False,
        )

        return Response({"message": "User created successfully. OTP sent to your email."}, status=status.HTTP_201_CREATED)

class OTPVerifyView(APIView):
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data["email"])

            # Check if OTP matches
            if user.otp != serializer.validated_data["otp"]:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if OTP is expired
            if user.otp_expiry and user.otp_expiry < timezone.now():
                return Response({"error": "OTP expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Mark user as verified and active
            user.is_verified = True
            user.is_active = True
            user.otp = None  # Clear OTP after verification
            user.otp_expiry = None
            user.save()

            # Generate JWT Tokens
            tokens = RefreshToken.for_user(user)
            return Response({
                "access": str(tokens.access_token),
                "refresh": str(tokens),
                "role": user.role
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if data["role"] == "user":
            return Response({
                "access": data["access"],
                "refresh": data["refresh"],
                "role": data["role"],
                "redirect": "/"
            }, status=status.HTTP_200_OK)
        elif data["role"] == "vendor":
            return Response({
                "access": data["access"],
                "refresh": data["refresh"],
                "role": data["role"],
                "redirect": "/vendor-dashboard"
            }, status=status.HTTP_200_OK)



class GoogleLoginView(APIView):
    def post(self, request):
        try:
            serializer = GoogleLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email = serializer.validated_data["email"]
            user, created = User.objects.get_or_create(email=email)

            if created:
                user.role = "user"  # Default role for Google login is 'user'
                user.is_verified = True  # Immediately verified for Google login
                user.is_active = True  # Immediately active for Google login
                user.save()

            # Send email notification
            send_mail(
                'Login Notification - AgroNepal',
                'You are logging in to AgroNepal. If this was not you, please contact support.',
                settings.EMAIL_HOST_USER,  # Sender's email (your Gmail address)
                [email],  # Recipient's email
                fail_silently=False,
            )

            tokens = RefreshToken.for_user(user)
            return Response({
                "access": str(tokens.access_token),
                "refresh": str(tokens),
                "role": user.role,
                "redirect": "user-dashboard"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({"error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")

            if not refresh_token:
                return Response({"error": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Attempt to blacklist the token

                return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)

            except TokenError as e:
                return Response({"error": f"Token error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
