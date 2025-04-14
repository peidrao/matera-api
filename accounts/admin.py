from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "document_number",
        "is_staff",
        "is_active",
    )
    search_fields = ("username", "email", "document_number")
    list_filter = ("is_staff", "is_superuser", "is_active")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Informações adicionais", {"fields": ("document_number",)}),
    )
