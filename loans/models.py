import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Loan(models.Model):
    # Identificador aleatório
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Usuário que pegou o empréstimo (para garantir a visibilidade restrita)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="loans")

    # Valor nominal
    principal_amount = models.DecimalField(max_digits=12, decimal_places=2)

    # Taxa de juros mensal (ex.: 0.02 para 2% ao mês)
    monthly_interest_rate = models.DecimalField(
        max_digits=5, decimal_places=4, default=0
    )

    # Endereço de IP (capturado no momento da criação)
    ip_address = models.GenericIPAddressField()

    # Data de solicitação
    requested_date = models.DateTimeField(default=timezone.now)

    # Banco
    bank = models.CharField(max_length=255)

    # Cliente
    client = models.CharField(max_length=255)

    def __str__(self):
        return f"Loan {self.id}"

    @property
    def total_paid(self):
        """Soma de todos os pagamentos recebidos."""
        return sum(payment.amount for payment in self.payments.all())

    @property
    def outstanding_balance(self):
        """Calcula o saldo devedor aproximado (juros simples, por exemplo)."""
        # Exemplo didático de juros simples mensais: principal + (principal * taxa * meses)
        # Ajuste conforme a regra de negócio.

        # Diferença em meses (muito simplificado)
        months_elapsed = (timezone.now().year - self.requested_date.year) * 12 + (
            timezone.now().month - self.requested_date.month
        )
        if months_elapsed < 0:
            months_elapsed = 0

        interest = (
            self.principal_amount * float(self.monthly_interest_rate) * months_elapsed
        )
        total_with_interest = self.principal_amount + interest
        return total_with_interest - self.total_paid
