from django.contrib import admin
from .models import Profile, PasswordResetToken


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "image_url")
    search_fields = ("user__username", "user__email")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at", "expires_at")
    readonly_fields = ("created_at",)