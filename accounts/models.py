from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    document = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="CPF/CNPJ",
        help_text="Número do CPF ou CNPJ",
    )

    def __str__(self):
        return f"{self.username} ({self.document})"
