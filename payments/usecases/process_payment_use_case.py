from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError, PermissionDenied
from payments.models import Payment
from loans.models import Loan


class ProcessPaymentUseCase:
    def __init__(self, *, loan: Loan, user, amount: Decimal):
        self.loan = loan
        self.user = user
        self.amount = amount

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

            if total_paid + self.amount >= total_due:
                loan.is_fully_paid = True
                loan.save(update_fields=["is_fully_paid"])

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
