from decimal import Decimal

from django.test import TestCase

from accounts.models import User
from accounts.usescases.get_account_use_case import GetAccountMeUseCase
from loans.models import Loan
from payments.models import Payment


class GetAccountMeUseCaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="client@example.com", password="12345678", document="11111111111"
        )
        self.usecase = GetAccountMeUseCase()

    def test_return_empty_summary_if_user_has_no_loans(self):
        data = self.usecase.handle(self.user)

        self.assertEqual(data["loans"]["total_loans"], 0)
        self.assertEqual(data["loans"]["fully_paid_loans"], 0)
        self.assertEqual(data["loans"]["active_loans"], 0)
        self.assertEqual(data["loans"]["principal_amount_total"], Decimal("0.00"))
        self.assertEqual(data["loans"]["amount_paid_total"], Decimal("0.00"))
        self.assertEqual(data["loans"]["outstanding_balance_total"], Decimal("0.00"))
        self.assertEqual(data["loans"]["percent_paid"], Decimal("0.00"))

    def test_user_with_one_unpaid_loan(self):
        Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            bank="Banco A",
            client="Cliente A",
        )

        result = self.usecase.handle(self.user)

        self.assertEqual(result["loans"]["total_loans"], 1)
        self.assertEqual(result["loans"]["fully_paid_loans"], 0)
        self.assertEqual(result["loans"]["active_loans"], 1)
        self.assertEqual(result["loans"]["principal_amount_total"], Decimal("1000.00"))
        self.assertEqual(result["loans"]["amount_paid_total"], Decimal("0.00"))
        self.assertGreater(
            result["loans"]["outstanding_balance_total"], Decimal("0.00")
        )
        self.assertEqual(result["loans"]["percent_paid"], Decimal("0.00"))

    def test_user_with_paid_and_unpaid_loans(self):
        loan1 = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.01"),
            ip_address="127.0.0.1",
            bank="Banco A",
            client="Cliente A",
        )
        loan2 = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("500.00"),
            monthly_interest_rate=Decimal("0.01"),
            ip_address="127.0.0.1",
            bank="Banco B",
            client="Cliente B",
            is_fully_paid=True,
        )
        Payment.objects.create(loan=loan1, amount=Decimal("300.00"))
        Payment.objects.create(loan=loan2, amount=Decimal("500.00"))

        result = self.usecase.handle(self.user)

        self.assertEqual(result["loans"]["total_loans"], 2)
        self.assertEqual(result["loans"]["fully_paid_loans"], 1)
        self.assertEqual(result["loans"]["active_loans"], 1)
        self.assertEqual(result["loans"]["amount_paid_total"], Decimal("800.00"))
        self.assertGreater(result["loans"]["percent_paid"], Decimal("0.00"))

    def test_rounding_behavior(self):
        loan = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("333.3333"),
            monthly_interest_rate=Decimal("0.01"),
            ip_address="127.0.0.1",
            bank="Banco Redondo",
            client="Cliente Redondo",
        )
        Payment.objects.create(loan=loan, amount=Decimal("123.4567"))

        result = self.usecase.handle(self.user)

        self.assertEqual(result["loans"]["principal_amount_total"], Decimal("333.33"))
        self.assertEqual(result["loans"]["amount_paid_total"], Decimal("123.46"))
