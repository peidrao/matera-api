from decimal import Decimal
from django.test import TestCase

from loans.models import Loan
from payments.models import Payment
from accounts.models import User


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com", password="12345678", document="12345678900"
        )
        self.loan = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            bank="Banco Teste",
            client="Cliente Teste",
        )

    def test_create_payment(self):
        payment = Payment.objects.create(
            loan=self.loan,
            amount=Decimal("250.00"),
        )

        self.assertEqual(payment.loan, self.loan)
        self.assertEqual(payment.amount, Decimal("250.00"))
        self.assertIsNotNone(payment.payment_date)
        self.assertIsNotNone(payment.created_at)
        self.assertIsInstance(payment.id, type(self.loan.id))
        self.assertEqual(str(payment), f"Payment {payment.id}")

    def test_default_amount_is_zero(self):
        payment = Payment.objects.create(loan=self.loan)
        self.assertEqual(payment.amount, Decimal("0.00"))

    def test_ordering_by_created_at(self):
        older = Payment.objects.create(loan=self.loan, amount=Decimal("100.00"))
        newer = Payment.objects.create(loan=self.loan, amount=Decimal("200.00"))

        payments = list(Payment.objects.all())
        self.assertEqual(payments[0], newer)
        self.assertEqual(payments[1], older)
