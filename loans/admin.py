from django.contrib import admin
from loans.models import Loan


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "client",
        "bank",
        "principal_amount",
        "monthly_interest_rate",
        "requested_date",
    )
    search_fields = ("client", "bank", "user__username")
    list_filter = ("bank", "requested_date")
    readonly_fields = (
        "created_at",
        "updated_at",
        "requested_date",
        "ip_address",
    )
