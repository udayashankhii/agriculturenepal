from django.urls import path
from .views import RegisterView, OTPVerifyView, LoginView, GoogleLoginView, LogoutView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", OTPVerifyView.as_view(), name="verify-otp"),
    path("login/", LoginView.as_view(), name="login"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path('logout/', LogoutView.as_view(), name='logout'),
]
