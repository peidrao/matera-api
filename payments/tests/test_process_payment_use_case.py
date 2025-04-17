from decimal import Decimal

from django.test import TestCase
from rest_framework.exceptions import PermissionDenied, ValidationError

from accounts.models import User
from loans.models import Loan
from payments.models import Payment
from payments.usecases.process_payment_use_case import ProcessPaymentUseCase


class ProcessPaymentUseCaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="payer@example.com", password="12345678", document="11111111111"
        )
        self.other_user = User.objects.create_user(
            email="invader@example.com", password="12345678", document="99999999999"
        )
        self.loan = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.01"),
            ip_address="127.0.0.1",
            bank="Banco XYZ",
            client="Cliente Legal",
        )
        self.usecase = ProcessPaymentUseCase()

    def test_successful_payment_does_not_fully_pay(self):
        payment = self.usecase.handle(
            loan=self.loan,
            user=self.user,
            amount=Decimal("300.00"),
            ip_address="10.0.0.1",
        )

        self.assertIsInstance(payment, Payment)
        self.assertEqual(payment.amount, Decimal("300.00"))
        self.loan.refresh_from_db()
        self.assertFalse(self.loan.is_fully_paid)

    def test_successful_payment_fully_pays_loan(self):
        amount_due = self.loan.total_due

        payment = self.usecase.handle(
            loan=self.loan, user=self.user, amount=amount_due, ip_address="10.0.0.1"
        )

        self.loan.refresh_from_db()
        self.assertTrue(self.loan.is_fully_paid)
        self.assertEqual(payment.amount, amount_due)

    def test_payment_exceeding_balance_raises_error(self):
        excess_amount = self.loan.total_due + Decimal("10.00")

        with self.assertRaises(ValidationError) as ctx:
            self.usecase.handle(loan=self.loan, user=self.user, amount=excess_amount)
        self.assertIn("O valor excede o saldo devedor", str(ctx.exception))

    def test_payment_on_already_paid_loan_raises_error(self):
        self.loan.is_fully_paid = True
        self.loan.save()

        with self.assertRaises(ValidationError) as ctx:
            self.usecase.handle(
                loan=self.loan, user=self.user, amount=Decimal("100.00")
            )
        self.assertIn("já está quitado", str(ctx.exception))

    def test_user_cannot_pay_loan_of_another_user(self):
        with self.assertRaises(PermissionDenied) as ctx:
            self.usecase.handle(
                loan=self.loan,
                user=self.other_user,
                amount=Decimal("100.00"),
            )
        self.assertIn("não tem permissão", str(ctx.exception))
