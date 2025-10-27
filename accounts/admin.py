from django.contrib import admin
from .models import User

class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "username", "phone_number", "role", "is_verified", "is_active", "otp", "otp_expiry", "last_login"]
    list_filter = ["role", "is_verified", "is_active"]
    search_fields = ["email", "username"]
    actions = ["verify_user", "send_otp"]

    def verify_user(self, request, queryset):
        """Action to verify selected users."""
        count = queryset.update(is_verified=True, is_active=True)
        self.message_user(request, f"{count} user(s) verified successfully.")

    def send_otp(self, request, queryset):
        """Action to send OTP to selected users."""
        for user in queryset:
            user.generate_otp()
        self.message_user(request, "OTP(s) sent successfully.")

    verify_user.short_description = "Mark selected users as verified"
    send_otp.short_description = "Send OTP to selected users"

admin.site.register(User, UserAdmin)
