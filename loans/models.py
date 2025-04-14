from decimal import Decimal
import uuid
from django.db import models
from django.utils import timezone

from accounts.models import User


class Loan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="loans")

    principal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    monthly_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal("0.0000")
    )

    ip_address = models.GenericIPAddressField()

    requested_date = models.DateTimeField(default=timezone.now)

    bank = models.CharField(max_length=255)

    client = models.CharField(max_length=255)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.id}"

    @property
    def total_paid(self):
        return self.payments.aggregate(total=models.Sum("amount"))["total"] or Decimal(
            "0.00"
        )

    @property
    def outstanding_balance(self):
        """Calcula saldo devedor com juros simples."""
        months_elapsed = (timezone.now().year - self.requested_date.year) * 12 + (
            timezone.now().month - self.requested_date.month
        )

        interest = (
            self.principal_amount * Decimal(self.monthly_interest_rate) * months_elapsed
        )
        total_due = self.principal_amount + interest
        return total_due - self.total_paid
