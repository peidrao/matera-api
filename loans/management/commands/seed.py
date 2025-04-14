import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User
from loans.models import Loan
from payments.models import Payment


fake = Faker("pt_BR")


class Command(BaseCommand):
    help = "Cria usuários, empréstimos e pagamentos fake para testes"

    def handle(self, *args, **kwargs):
        user = User.objects.create_user(
            username="admin",
            email="admin@admin.com",
            password="12345678",
            document="12345678909",
        )

        self.stdout.write(self.style.SUCCESS(f"Usuário criado: {user.username}"))

        for _ in range(random.randint(1, 3)):
            loan = Loan.objects.create(
                user=user,
                principal_amount=Decimal(random.randint(1000, 10000)),
                monthly_interest_rate=Decimal("0.02"),
                ip_address=fake.ipv4(),
                requested_date=fake.date_time_this_year(),
                bank=fake.company(),
                client=fake.name(),
            )

            self.stdout.write(f"  Empréstimo criado: {loan.id}")

            for _ in range(random.randint(1, 4)):
                Payment.objects.create(
                    loan=loan,
                    amount=Decimal(random.randint(100, 1000)),
                    payment_date=fake.date_time_between(start_date=loan.requested_date),
                )

            self.stdout.write("Pagamentos adicionados")
