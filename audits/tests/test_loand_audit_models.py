from django.test import TestCase
from decimal import Decimal
from uuid import UUID

from accounts.models import User
from loans.models import Loan
from audits.models import LoanAuditLog
from audits.enums.loan_audit_enum import LoanActionEnum


class LoanAuditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="log@test.com", password="12345678", document="12345678900"
        )
        self.loan = Loan.objects.create(
            user=self.user,
            principal_amount=Decimal("1500.00"),
            monthly_interest_rate=Decimal("0.02"),
            ip_address="192.168.0.10",
            bank="Banco Log",
            client="Cliente Log",
        )

    def test_create_log_with_all_fields(self):
        log = LoanAuditLog.objects.create(
            loan=self.loan,
            action=LoanActionEnum.CREATED,
            performed_by=self.user,
            ip_address="127.0.0.1",
            metadata={"key": "value"},
        )

        self.assertIsInstance(log.id, UUID)
        self.assertEqual(log.loan, self.loan)
        self.assertEqual(log.action, LoanActionEnum.CREATED)
        self.assertEqual(log.performed_by, self.user)
        self.assertEqual(log.ip_address, "127.0.0.1")
        self.assertEqual(log.metadata, {"key": "value"})
        self.assertIsNotNone(log.timestamp)
        self.assertEqual(str(log), f"[{log.action}] {self.loan.id} by {self.user}")

    def test_log_with_null_ip_and_empty_metadata(self):
        log = LoanAuditLog.objects.create(
            loan=self.loan,
            action=LoanActionEnum.CLOSED,
            performed_by=self.user,
        )

        self.assertIsNone(log.ip_address)
        self.assertEqual(log.metadata, {})

    def test_log_with_null_user(self):
        log = LoanAuditLog.objects.create(
            loan=self.loan,
            action=LoanActionEnum.PAYMENT,
            performed_by=None,
            ip_address="10.0.0.1",
        )

        self.assertIsNone(log.performed_by)
        self.assertEqual(log.action, LoanActionEnum.PAYMENT)
        self.assertEqual(str(log), f"[{log.action}] {self.loan.id} by None")

    def test_str_representation(self):
        log = LoanAuditLog.objects.create(
            loan=self.loan,
            action=LoanActionEnum.CREATED,
            performed_by=self.user,
            ip_address="127.0.0.1",
        )

        expected = f"[{LoanActionEnum.CREATED}] {self.loan.id} by {self.user}"
        self.assertEqual(str(log), expected)
