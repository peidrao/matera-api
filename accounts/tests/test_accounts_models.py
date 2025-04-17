from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class CustomUserModelTest(TestCase):
    def test_create_user_with_email_and_document(self):
        user = User.objects.create_user(
            email="user@example.com", password="12345678", document="12345678900"
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertTrue(user.check_password("12345678"))
        self.assertEqual(user.document, "12345678900")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser_success(self):
        admin = User.objects.create_superuser(
            email="admin@example.com", password="adminpass", document="00000000000"
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.email, "admin@example.com")
        self.assertTrue(admin.check_password("adminpass"))

    def test_create_user_without_email_raises_error(self):
        with self.assertRaisesMessage(ValueError, "O e-mail é obrigatório"):
            User.objects.create_user(email=None, password="123", document="111")

    def test_create_superuser_without_is_staff_raises_error(self):
        with self.assertRaisesMessage(
            ValueError, "Superuser precisa ter is_staff=True."
        ):
            User.objects.create_superuser(
                email="admin@fail.com",
                password="failpass",
                document="0001",
                is_staff=False,
            )

    def test_create_superuser_without_is_superuser_raises_error(self):
        with self.assertRaisesMessage(
            ValueError, "Superuser precisa ter is_superuser=True."
        ):
            User.objects.create_superuser(
                email="admin@fail.com",
                password="failpass",
                document="0002",
                is_superuser=False,
            )

    def test_str_representation(self):
        user = User.objects.create_user(
            email="str@example.com", password="123", document="99999999999"
        )
        self.assertEqual(str(user), "str@example.com (99999999999)")

    def test_unique_email_constraint(self):
        User.objects.create_user(
            email="duplicate@example.com", password="123", document="123"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="duplicate@example.com", password="123", document="456"
            )

    def test_unique_document_constraint(self):
        User.objects.create_user(
            email="unique1@example.com", password="123", document="cpf-001"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                email="unique2@example.com", password="123", document="cpf-001"
            )
