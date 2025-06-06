from django.contrib.auth.models import AbstractUser
from django.db import models
from simple_history.models import HistoricalRecords

from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    document = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="CPF/CNPJ",
        help_text="Número do CPF ou CNPJ",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    history = HistoricalRecords()

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} ({self.document})"
