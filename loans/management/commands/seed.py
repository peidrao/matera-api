import random
from decimal import Decimal
from django.utils.timezone import make_aware

from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User
from loans.models import Loan
from payments.models import Payment


fake = Faker("pt_BR")


class Command(BaseCommand):
    help = "Cria usuários, empréstimos e pagamentos fake para testes"

    def handle(self, *args, **kwargs):
        user = User.objects.create(
            email="admin@admin.com",
            password="12345678",
            document="12345678909",
        )

        self.stdout.write(self.style.SUCCESS(f"Usuário criado: {user.email}"))

        for _ in range(random.randint(10, 20)):
            requested_date = make_aware(fake.date_time_this_year())
            loan = Loan.objects.create(
                user=user,
                principal_amount=Decimal(random.randint(1000, 10000)),
                monthly_interest_rate=Decimal("0.02"),
                ip_address=fake.ipv4(),
                requested_date=requested_date,
                bank=fake.company(),
                client=fake.name(),
            )

            self.stdout.write(f"Empréstimo criado: {loan.id}")

            for _ in range(random.randint(1, 4)):
                payment_date = make_aware(
                    fake.date_time_between(start_date=loan.requested_date)
                )
                Payment.objects.create(
                    loan=loan,
                    amount=Decimal(random.randint(100, 1000)),
                    payment_date=payment_date,
                )

            self.stdout.write("Pagamentos adicionados")
