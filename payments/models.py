from time import timezone
from django.db import models

from loans.models import Loan


class Payment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Payment {self.id} for Loan {self.loan.id}"
