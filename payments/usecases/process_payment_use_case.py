from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import User
from audits.enums import LoanActionEnum
from audits.services import log_loan_action
from loans.models import Loan
from payments.models import Payment


class ProcessPaymentUseCase:
    """
    Caso de uso responsável por processar um pagamento de um empréstimo.
    """

    def handle(
        self, loan: Loan, user: User, amount: Decimal, ip_address=None
    ) -> Payment:
        """
        Executa o caso de uso de pagamento.

        1. Realiza validações de integridade e autorização.
        2. Garante atomicidade da operação usando `transaction.atomic()`.
        3. Cria o pagamento e registra log de auditoria.
        4. Se o valor total pago atinge ou ultrapassa o valor devido, marca o
            empréstimo como quitado.
        5. Retorna a instância de Payment criada.
        """
        # 1
        self._validate(loan=loan, user=user, amount=amount)

        # 2
        with transaction.atomic():
            loan = (
                Loan.objects.select_for_update()
                .select_related("user")
                .get(
                    id=loan.id,
                )
            )

            # 3
            total_paid = loan.payments.aggregate(total=Sum("amount"))[
                "total"
            ] or Decimal("0.00")
            total_due = loan.total_due

            payment = Payment.objects.create(loan=loan, amount=amount)

            log_loan_action(
                loan=loan,
                action=LoanActionEnum.PAYMENT,
                user=user,
                ip_address=ip_address,
                metadata={
                    "amount": str(amount),
                    "total_paid_before": str(total_paid),
                    "total_due": str(total_due),
                },
            )

            # 4
            if total_paid + amount >= total_due:
                loan.is_fully_paid = True
                loan.save(update_fields=["is_fully_paid"])

                log_loan_action(
                    loan=loan,
                    action=LoanActionEnum.CLOSED,
                    user=user,
                    ip_address=ip_address,
                    metadata={
                        "reason": "Empréstimo totalmente quitado",
                        "total_paid": str(total_paid + amount),
                    },
                )

            # 5
            return payment

    def _validate(self, loan: Loan, user: User, amount: Decimal):
        """
        Realiza validações antes de prosseguir com o pagamento.

        1. Verifica se o empréstimo pertence ao usuário autenticado.
        2. Verifica se o empréstimo já está quitado.
        3. Verifica se o valor a pagar ultrapassa o total devido.
        """
        # 1
        if loan.user != user:
            raise PermissionDenied("Você não tem permissão para pagar este empréstimo.")

        # 2
        if loan.is_fully_paid:
            raise ValidationError({"detail": "Este empréstimo já está quitado."})

        # 3
        total_paid = loan.payments.aggregate(total=Sum("amount"))["total"] or Decimal(
            "0.00"
        )
        total_due = loan.total_due

        if total_paid + amount > total_due:
            raise ValidationError({"detail": "O valor excede o saldo devedor."})
