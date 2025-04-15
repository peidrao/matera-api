import uuid

from django.db import models

from accounts.models import User
from audits.enums.loan_audit_enum import LoanActionEnum
from loans.models import Loan


class LoanAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name="logs")
    action = models.CharField(max_length=20, choices=LoanActionEnum.choices)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.action}] {self.loan.id} by {self.performed_by}"
