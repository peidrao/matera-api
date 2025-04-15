from decimal import Decimal, ROUND_HALF_UP
from functools import cached_property
from django.db import models
from django.utils.timezone import now
from accounts.models import User


class Loan(models.Model):
    """
    Representa um contrato de empréstimo entre um cliente e um banco.

    Cálculos automáticos:
    - Juros compostos pro rata dia
    - IOF fixo + IOF diário
    - Seguro baseado em percentual
    - Saldo devedor dinâmico
    """

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="loans",
    )
    principal_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    monthly_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal("0.0000")
    )
    ip_address = models.GenericIPAddressField()
    requested_date = models.DateTimeField(auto_now_add=True)
    bank = models.CharField(max_length=255)
    client = models.CharField(max_length=255)
    is_fully_paid = models.BooleanField(default=False)
    insurance_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=Decimal("0.01")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.id}"

    @cached_property
    def total_paid(self):
        """Soma de todos os pagamentos realizados para este empréstimo."""
        return sum(payment.amount for payment in self.payments.all())

    @cached_property
    def days_since_requested(self):
        """Número de dias desde a data de solicitação."""
        return (now().date() - self.requested_date.date()).days

    @property
    def compounded_amount(self):
        """
        Valor do empréstimo com aplicação de juros compostos pro rata dia.
        Fórmula: M = P * (1 + i)^n, onde i é a taxa diária.
        """
        if self.days_since_requested <= 0:
            return self.principal_amount
        daily_rate = (1 + self.monthly_interest_rate) ** (Decimal("1") / 30) - 1
        compounded = (
            self.principal_amount * (1 + daily_rate) ** self.days_since_requested
        )
        return compounded.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def iof(self):
        """
        Cálculo do IOF total (fixo + diário), limitado a 365 dias ou 3%.
        IOF fixo: 0.38% do valor
        IOF diário: 0.0082% por dia (máx. 3%)
        """
        dias = min(self.days_since_requested, 365)
        iof_diario = self.principal_amount * Decimal("0.000082") * dias
        iof_fixo = self.principal_amount * Decimal("0.0038")
        total_iof = iof_diario + iof_fixo
        return total_iof.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def insurance(self):
        """Valor do seguro sobre o empréstimo (default 1%)."""
        return (self.principal_amount * self.insurance_rate).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

    @property
    def total_due(self):
        """Valor total atualizado do empréstimo com juros, IOF e seguro."""
        return (self.compounded_amount + self.iof + self.insurance).quantize(
            Decimal("0.01")
        )

    @property
    def outstanding_balance(self):
        """Saldo devedor: valor total menos o que já foi pago."""
        return max(self.total_due - self.total_paid, Decimal("0.00"))
