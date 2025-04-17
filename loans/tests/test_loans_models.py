from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.test import TestCase
from django.utils.timezone import now

from accounts.models import User
from loans.models import Loan
from payments.models import Payment


class LoanModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", password="12345678", document="12345678900"
        )
        self.loan = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            bank="Banco Central",
            client="Cliente Teste",
            insurance_rate=Decimal("0.01"),
        )

        self.loan.requested_date = now() - timedelta(days=30)
        self.loan.save(update_fields=["requested_date"])

    def test_str_representation(self):
        self.assertEqual(str(self.loan), f"Loan {self.loan.id}")

    def test_total_paid_with_no_payments(self):
        self.assertEqual(self.loan.total_paid, Decimal("0.00"))

    def test_total_paid_with_multiple_payments(self):
        Payment.objects.create(loan=self.loan, amount=Decimal("300.00"))
        Payment.objects.create(loan=self.loan, amount=Decimal("200.00"))
        self.assertEqual(self.loan.total_paid, Decimal("500.00"))

    def test_days_since_requested(self):
        expected_days = 30
        self.assertEqual(self.loan.days_since_requested, expected_days)

    def test_compounded_amount(self):
        compounded = self.loan.compounded_amount
        self.assertIsInstance(compounded, Decimal)
        self.assertGreater(compounded, self.loan.principal_amount)

    def test_compounded_amount_same_day(self):
        loan_today = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            requested_date=now(),
            bank="Banco Teste",
            client="Cliente Hoje",
        )
        self.assertEqual(loan_today.compounded_amount, Decimal("1000.00"))

    def test_iof_calculation(self):
        expected_iof = (
            self.loan.principal_amount * Decimal("0.000082") * 30
            + self.loan.principal_amount * Decimal("0.0038")
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        self.assertEqual(self.loan.iof, expected_iof)

    def test_iof_max_days(self):
        loan_ano = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            requested_date=now() - timedelta(days=400),
            bank="Banco Teste",
            client="Cliente 400 dias",
        )
        self.assertLessEqual(loan_ano.iof, Decimal("30.00"))  # limite de 3%

    def test_insurance(self):
        expected = self.loan.principal_amount * self.loan.insurance_rate
        self.assertEqual(self.loan.insurance, expected.quantize(Decimal("0.01")))

    def test_total_due(self):
        total = self.loan.total_due
        self.assertIsInstance(total, Decimal)
        self.assertGreater(total, self.loan.principal_amount)

    def test_outstanding_balance_with_no_payments(self):
        self.assertEqual(
            self.loan.outstanding_balance, self.loan.total_due - self.loan.total_paid
        )

    def test_outstanding_balance_with_partial_payment(self):
        Payment.objects.create(loan=self.loan, amount=Decimal("200.00"))
        expected = max(self.loan.total_due - Decimal("200.00"), Decimal("0.00"))
        self.assertEqual(self.loan.outstanding_balance, expected)

    def test_outstanding_balance_after_full_payment(self):
        Payment.objects.create(loan=self.loan, amount=self.loan.total_due)
        self.assertEqual(self.loan.outstanding_balance, Decimal("0.00"))
