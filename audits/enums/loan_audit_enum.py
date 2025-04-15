from django.db import models


class LoanActionEnum(models.TextChoices):
    CREATED = "created", "Criado"
    UPDATED = "updated", "Atualizado"
    PAYMENT = "payment", "Pagamento"
    CLOSED = "closed", "Quitado"
