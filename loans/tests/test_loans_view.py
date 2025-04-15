import datetime
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from loans.models import Loan


class LoanViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user1@test.com", password="12345678", document="11111111111"
        )
        self.other_user = User.objects.create_user(
            email="user2@test.com", password="12345678", document="22222222222"
        )

        self.client.force_authenticate(user=self.user)

        self.loan1 = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1000.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="127.0.0.1",
            requested_date=make_aware(datetime.datetime.now()),
            bank="Banco A",
            client="Cliente A",
        )

        self.loan2 = Loan.objects.create(
            user=self.other_user,
            principal_amount=Decimal("2000.00"),
            monthly_interest_rate=Decimal("0.03"),
            ip_address="127.0.0.1",
            requested_date=make_aware(datetime.datetime.now()),
            bank="Banco B",
            client="Cliente B",
        )

    def test_authenticated_user_can_list_only_own_loans(self):
        response = self.client.get(reverse("loans-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["principal_amount"],
            "1000.00",
        )

    def test_create_loan_successfully(self):
        data = {
            "principal_amount": "1500.00",
            "monthly_interest_rate": "0.025",
            "bank": "Banco C",
            "client": "Cliente C",
        }
        response = self.client.post(reverse("loans-list"), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.data["principal_amount"], "1500.00")
        self.assertEqual(response.data["bank"], "Banco C")

    def test_unauthenticated_user_cannot_access(self):
        self.client.logout()
        response = self.client.get(reverse("loans-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_loan_creation_sets_user_and_ip(self):
        data = {
            "principal_amount": "2000.00",
            "monthly_interest_rate": "0.015",
            "bank": "Banco D",
            "client": "Cliente D",
        }

        response = self.client.post(reverse("loans-list"), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        loan = Loan.objects.get(id=response.data["id"])
        self.assertEqual(loan.user, self.user)
        self.assertEqual(loan.ip_address, "127.0.0.1")
