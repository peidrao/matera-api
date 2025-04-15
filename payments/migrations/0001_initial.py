# Generated by Django 5.2 on 2025-04-15 14:59

import django.db.models.deletion
import django.utils.timezone
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("loans", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "payment_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "amount",
                    models.DecimalField(
                        decimal_places=2, default=Decimal("0.00"), max_digits=12
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "loan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="payments",
                        to="loans.loan",
                    ),
                ),
            ],
            options={
                "ordering": ["-payment_date"],
            },
        ),
    ]
