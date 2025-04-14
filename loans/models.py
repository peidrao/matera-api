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
        """Soma de todos os pagamentos recebidos."""
        return sum(payment.amount for payment in self.payments.all())
