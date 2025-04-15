from django.contrib import admin
from .models import LoanAuditLog


@admin.register(LoanAuditLog)
class LoanLogAdmin(admin.ModelAdmin):
    list_display = ("loan", "action", "performed_by", "timestamp")
    search_fields = ("loan__id", "performed_by__email")
    list_filter = ("action", "timestamp")
