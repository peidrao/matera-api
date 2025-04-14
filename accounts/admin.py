from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "document",
        "is_staff",
        "is_active",
    )
    search_fields = ("email", "document")
    list_filter = ("is_staff", "is_superuser", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Informações adicionais", {"fields": ("document",)}),
    )
