from decimal import Decimal, ROUND_HALF_UP
from loans.models import Loan
from payments.models import Payment
from django.db.models import Sum


def quantize_2(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def get_user_me(user):
    loans = Loan.objects.filter(user=user)
    total_loans = loans.count()
    fully_paid = loans.filter(is_fully_paid=True).count()
    principal_total = loans.aggregate(total=Sum("principal_amount"))[
        "total"
    ] or Decimal("0.00")
    payments_total = Payment.objects.filter(loan__user=user).aggregate(
        total=Sum("amount")
    )["total"] or Decimal("0.00")

    debt_total = sum((loan.outstanding_balance + loan.total_paid) for loan in loans)
    percent_paid = (
        (payments_total / debt_total * 100) if debt_total > 0 else Decimal("0.00")
    )

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
            "principal_amount_total": quantize_2(principal_total),
            "amount_paid_total": quantize_2(payments_total),
            "outstanding_balance_total": quantize_2(debt_total - payments_total),
            "percent_paid": quantize_2(percent_paid),
        },
    }
