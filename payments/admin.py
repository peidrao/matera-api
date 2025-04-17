from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = (
        "id",
        "loan",
        "amount",
        "payment_date",
        "created_at",
    )
    search_fields = ("loan__client", "loan__bank", "loan__user__email")
    list_filter = ("payment_date",)
    readonly_fields = ("created_at",)
