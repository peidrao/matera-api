import datetime
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from loans.models import Loan
from payments.models import Payment


class PaymentViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@test.com", password="12345678", document="11111111111"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", password="12345678", document="22222222222"
        )

        self.client.force_authenticate(user=self.user)

        self.loan = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            requested_date=make_aware(datetime.datetime.now()),
            bank="Banco XP",
            client="Cliente XP",
        )

        self.other_loan = Loan.objects.create(
            user=self.other_user,
            principal_amount=Decimal("2000.00"),
            monthly_interest_rate=Decimal("0.03"),
            ip_address="127.0.0.1",
            requested_date=make_aware(datetime.datetime.now()),
            bank="Banco Y",
            client="Cliente Y",
        )

    def test_create_payment_successfully(self):
        response = self.client.post(
            reverse("payments-list"),
            {
                "loan": str(self.loan.id),
                "amount": "300.00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)

    def test_user_cannot_create_payment_for_another_users_loan(self):
        response = self.client.post(
            reverse("payments-list"),
            {"loan": str(self.other_loan.id), "amount": "300.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Payment.objects.count(), 0)

    def test_payment_marks_loan_as_fully_paid(self):
        Payment.objects.create(loan=self.loan, amount=Decimal("900.00"))
        self.client.post(
            reverse("payments-list"),
            {
                "loan": str(self.loan.id),
                "amount": "200.00",
            },
        )
        self.loan.refresh_from_db()
        self.assertTrue(self.loan.is_fully_paid)

    def test_payment_fails_if_loan_is_already_paid(self):
        self.loan.is_fully_paid = True
        self.loan.save()
        response = self.client.post(
            reverse("payments-list"),
            {
                "loan": str(self.loan.id),
                "amount": "100.00",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", response.data)

    def test_list_only_payments_for_authenticated_user(self):
        Payment.objects.create(loan=self.loan, amount=Decimal("500.00"))
        Payment.objects.create(loan=self.other_loan, amount=Decimal("500.00"))

        response = self.client.get(reverse("payments-list"))
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["amount"], "500.00")
