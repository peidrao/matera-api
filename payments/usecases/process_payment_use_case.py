from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import PermissionDenied, ValidationError

from audits.enums import LoanActionEnum
from audits.services import log_loan_action
from loans.models import Loan
from payments.models import Payment


class ProcessPaymentUseCase:
    def __init__(self, *, loan: Loan, user, amount: Decimal, ip_address=None):
        self.loan = loan
        self.user = user
        self.amount = amount
        self.ip_address = ip_address

    def handle(self) -> Payment:
        self._validate()

        with transaction.atomic():
            loan = (
                Loan.objects.select_for_update()
                .select_related("user")
                .get(id=self.loan.id)
            )

            total_paid = loan.payments.aggregate(total=Sum("amount"))[
                "total"
            ] or Decimal("0.00")
            total_due = loan.total_due

            payment = Payment.objects.create(loan=loan, amount=self.amount)

            log_loan_action(
                loan=loan,
                action=LoanActionEnum.PAYMENT,
                user=self.user,
                ip_address=self.ip_address,
                metadata={
                    "amount": str(self.amount),
                    "total_paid_before": str(total_paid),
                    "total_due": str(total_due),
                },
            )

            if total_paid + self.amount >= total_due:
                loan.is_fully_paid = True
                loan.save(update_fields=["is_fully_paid"])

                log_loan_action(
                    loan=loan,
                    action=LoanActionEnum.CLOSED,
                    user=self.user,
                    ip_address=self.ip_address,
                    metadata={
                        "reason": "Empréstimo totalmente quitado",
                        "total_paid": str(total_paid + self.amount),
                    },
                )

            return payment

    def _validate(self):
        if self.loan.user != self.user:
            raise PermissionDenied(
                "Você não tem permissão para pagar este empréstimo.",
            )

        if self.loan.is_fully_paid:
            raise ValidationError({"detail": "Este empréstimo já está quitado."})

        total_paid = self.loan.payments.aggregate(total=Sum("amount"))[
            "total"
        ] or Decimal("0.00")
        total_due = self.loan.total_due

        if total_paid + self.amount > total_due:
            raise ValidationError({"detail": "O valor excede o saldo devedor."})
