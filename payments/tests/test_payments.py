import datetime
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import make_aware
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from audits.enums.loan_audit_enum import LoanActionEnum
from audits.models.loan_audit_model import LoanAuditLog
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
            {"loan": str(self.loan.id), "amount": "300.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)

        logs = LoanAuditLog.objects.filter(
            loan=self.loan, action=LoanActionEnum.PAYMENT
        )
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().performed_by, self.user)

    def test_user_cannot_create_payment_for_another_users_loan(self):
        response = self.client.post(
            reverse("payments-list"),
            {"loan": str(self.other_loan.id), "amount": "300.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Payment.objects.count(), 0)

        logs = LoanAuditLog.objects.filter(loan=self.other_loan)
        self.assertEqual(logs.count(), 0)

    def test_create_loan_and_fully_pay_it(self):
        loan_response = self.client.post(
            reverse("loans-list"),
            {
                "principal_amount": "1000.00",
                "monthly_interest_rate": "0.02",
                "bank": "Banco Teste",
                "client": "Cliente Teste",
            },
        )
        self.assertEqual(loan_response.status_code, status.HTTP_201_CREATED)
        loan_id = loan_response.data["id"]
        loan = Loan.objects.get(id=loan_id)
        total_due = loan.total_due.quantize(Decimal("0.01"))

        payment_response = self.client.post(
            reverse("payments-list"),
            {"loan": str(loan.id), "amount": str(total_due)},
        )
        self.assertEqual(payment_response.status_code, status.HTTP_201_CREATED)
        loan.refresh_from_db()
        self.assertTrue(loan.is_fully_paid)

        logs = LoanAuditLog.objects.filter(loan=loan)
        self.assertTrue(logs.filter(action=LoanActionEnum.CREATED).exists())
        self.assertTrue(logs.filter(action=LoanActionEnum.PAYMENT).exists())
        self.assertTrue(logs.filter(action=LoanActionEnum.CLOSED).exists())

    def test_payment_fails_if_loan_is_already_paid(self):
        self.loan.is_fully_paid = True
        self.loan.save()

        response = self.client.post(
            reverse("payments-list"),
            {"loan": str(self.loan.id), "amount": "100.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        logs = LoanAuditLog.objects.filter(loan=self.loan)
        self.assertEqual(logs.count(), 0)

    def test_list_only_payments_for_authenticated_user(self):
        Payment.objects.create(loan=self.loan, amount=Decimal("500.00"))
        Payment.objects.create(loan=self.other_loan, amount=Decimal("500.00"))

        response = self.client.get(reverse("payments-list"))

        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["amount"], "500.00")

    def test_cannot_pay_more_than_total_due(self):
        total_due = self.loan.total_due
        Payment.objects.create(loan=self.loan, amount=total_due - Decimal("10.00"))

        response = self.client.post(
            reverse("payments-list"),
            {"loan": str(self.loan.id), "amount": "20.00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        logs = LoanAuditLog.objects.filter(
            loan=self.loan, action=LoanActionEnum.PAYMENT
        )
        self.assertEqual(logs.count(), 0)

    def test_multiple_partial_payments_should_fully_pay_loan(self):
        self.loan.refresh_from_db()
        total_due = self.loan.total_due
        part = (total_due / 3).quantize(Decimal("0.01"))

        for _ in range(2):
            response = self.client.post(
                reverse("payments-list"),
                {"loan": str(self.loan.id), "amount": str(part)},
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        remaining = (total_due - part * 2).quantize(Decimal("0.01"))
        response = self.client.post(
            reverse("payments-list"),
            {"loan": str(self.loan.id), "amount": str(remaining)},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.loan.refresh_from_db()
        self.assertTrue(self.loan.is_fully_paid)

        logs = LoanAuditLog.objects.filter(loan=self.loan)
        self.assertEqual(logs.filter(action=LoanActionEnum.PAYMENT).count(), 3)
        self.assertTrue(logs.filter(action=LoanActionEnum.CLOSED).exists())

    def test_simulated_concurrent_payments_should_not_exceed_total_due(self):
        self.loan.refresh_from_db()
        total_due = self.loan.total_due
        half = (total_due / 2).quantize(Decimal("0.01"))

        response_1 = self.client.post(
            reverse("payments-list"),
            {"loan": str(self.loan.id), "amount": str(half)},
        )
        response_2 = self.client.post(
            reverse("payments-list"),
            {"loan": str(self.loan.id), "amount": str(half + Decimal("0.01"))},
        )

        self.assertEqual(response_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_2.status_code, status.HTTP_400_BAD_REQUEST)

        logs = LoanAuditLog.objects.filter(
            loan=self.loan, action=LoanActionEnum.PAYMENT
        )
        self.assertEqual(logs.count(), 1)
