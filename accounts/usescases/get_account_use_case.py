from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Sum

from accounts.models import User
from loans.models import Loan
from payments.models import Payment


class GetAccountMeUseCase:
    """
    Caso de uso responsável por retornar o resumo financeiro de um usuário
    autenticado.

    Etapas do processo:
        1. Buscar os empréstimos do usuário
        2. Calcular totais e quantidades de status dos empréstimos
        3. Calcular total de pagamentos
        4. Calcular dívida total (saldo + já pago)
        5. Calcular o percentual pago
        6. Arredondar os valores para duas casas decimais
        7. Retornar os dados consolidados
    """

    def handle(self, user: User) -> dict:
        """
        Executa o fluxo de consolidação dos dados financeiros do usuário.
        """

        # 1
        loans = Loan.objects.filter(user=user)

        # 2
        total_loans = loans.count()
        fully_paid = loans.filter(is_fully_paid=True).count()

        # 3
        principal_total = loans.aggregate(total=Sum("principal_amount"))[
            "total"
        ] or Decimal("0.00")

        # 4
        payments_total = Payment.objects.filter(loan__user=user).aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

        # 5
        debt_total = sum((loan.outstanding_balance + loan.total_paid) for loan in loans)

        # 6
        percent_paid = (
            (payments_total / debt_total * 100) if debt_total > 0 else Decimal("0.00")
        )

        # 7
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "document": user.document,
                "created_at": user.date_joined,
            },
            "loans": {
                "total_loans": total_loans,
                "fully_paid_loans": fully_paid,
                "active_loans": total_loans - fully_paid,
                "principal_amount_total": self._quantitize(principal_total),
                "amount_paid_total": self._quantitize(payments_total),
                "outstanding_balance_total": self._quantitize(
                    debt_total - payments_total
                ),
                "percent_paid": self._quantitize(percent_paid),
            },
        }

    def _quantitize(self, value: Decimal) -> Decimal:
        """
        Arredonda um valor decimal para duas casas usando ROUND_HALF_UP.
        """
        return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
