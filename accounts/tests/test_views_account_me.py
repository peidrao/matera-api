import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from loans.models import Loan
from payments.models import Payment


class MeEndpointTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com", password="12345678", document="12345678900"
        )
        self.client.force_authenticate(user=self.user)

        self.loan1 = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            requested_date=make_aware(datetime.datetime.now()),
            bank="Banco XP",
            client="Cliente A",
        )

        self.loan2 = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("2000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            requested_date=make_aware(datetime.datetime.now()),
            bank="Banco XP",
            client="Cliente B",
            is_fully_paid=True,
        )

        Payment.objects.create(loan=self.loan1, amount=Decimal("300.00"))
        Payment.objects.create(loan=self.loan1, amount=Decimal("200.00"))
        Payment.objects.create(loan=self.loan2, amount=Decimal("2000.00"))

    def test_authenticated_user_receives_summary(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("user", response.data)
        self.assertIn("loans", response.data)

    def test_loan_counts_are_correct(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.data["loans"]["total_loans"], 2)
        self.assertEqual(response.data["loans"]["fully_paid_loans"], 1)
        self.assertEqual(response.data["loans"]["active_loans"], 1)

    def test_financial_totals_are_correct(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(
            Decimal(response.data["loans"]["principal_amount_total"]),
            Decimal("3000.00"),
        )
        self.assertEqual(
            Decimal(response.data["loans"]["amount_paid_total"]),
            Decimal(
                "2500.00",
            ),
        )

    def test_unauthenticated_user_cannot_access(self):
        self.client.logout()
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
