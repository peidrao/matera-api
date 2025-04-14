from decimal import Decimal
from django.db import models
from django.utils import timezone

from loans.models import Loan


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name="payments")
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Payment {self.id}"
