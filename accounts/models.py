from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import random

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = models.CharField(max_length=255, unique=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=False,)
    role = models.CharField(max_length=10, choices=[("vendor", "Vendor"), ("user", "User")], default="user")
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "phone_number"]

    objects = UserManager()

    def generate_otp(self):
        """Generate OTP for user."""
        self.otp = str(random.randint(100000, 999999))
        self.otp_expiry = timezone.now() + timezone.timedelta(minutes=10)
        self.save()

    @property
    def is_profile_complete(self):
        """Check if the user has completed profile setup."""
        return bool(self.phone_number and self.role)

    def __str__(self):
        return self.email
