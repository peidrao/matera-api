import uuid

from decimal import Decimal
from django.db import models
from django.utils import timezone

from loans.models import Loan


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    loan = models.ForeignKey(
        Loan, on_delete=models.PROTECT, db_index=True, related_name="payments"
    )
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id}"
