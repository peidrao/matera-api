from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from audits.enums import LoanActionEnum
from audits.services import log_loan_action

from .models import Loan
from .serializers import LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Loan.objects.filter(user=self.request.user)
            .select_related("user")
            .order_by("-created_at")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        ip = self.request.META.get("REMOTE_ADDR", "127.0.0.1")
        loan = serializer.save(user=self.request.user, ip_address=ip)

        log_loan_action(
            loan=loan,
            action=LoanActionEnum.CREATED,
            user=self.request.user,
            ip_address=ip,
            metadata={
                "principal_amount": str(loan.principal_amount),
                "interest": str(loan.monthly_interest_rate),
                "bank": loan.bank,
            },
        )
