from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from simple_history.admin import (
    SimpleHistoryAdmin,
)

from accounts.models import User


@admin.register(User)
class UserAdmin(SimpleHistoryAdmin, BaseUserAdmin):
    ordering = ["email"]
    list_display = ("email", "document", "is_staff", "is_active")
    search_fields = ("email", "document")
    list_filter = ("is_staff", "is_superuser", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Informações pessoais"), {"fields": ("document",)}),
        (
            _("Permissões"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Datas importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "document", "password1", "password2"),
            },
        ),
    )
