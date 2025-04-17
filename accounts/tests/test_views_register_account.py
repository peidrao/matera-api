from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from accounts.serializers import RegisterSerializer


class RegisterViewTestCase(APITestCase):
    def setUp(self):
        self.url = reverse("register")
        self.valid_payload = {
            "email": "newuser@example.com",
            "password": "strongpassword123",
            "document": "12345678900",
        }

    def test_register_user_successfully(self):
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().email, self.valid_payload["email"])

    def test_document_must_be_only_digits(self):
        data = {
            "email": "user@example.com",
            "password": "12345678",
            "document": "abc123456",
        }

        serializer = RegisterSerializer(data=data)
        is_valid = serializer.is_valid()

        self.assertFalse(is_valid)
        self.assertIn("document", serializer.errors)
        self.assertIn(
            "O CPF/CNPJ deve conter apenas números.", serializer.errors["document"]
        )

    def test_register_missing_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("password", response.data)
        self.assertIn("document", response.data)

    def test_register_duplicate_email(self):
        User.objects.create_user(
            email=self.valid_payload["email"],
            password="otherpass123",
            document="99999999999",
        )
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_duplicate_document(self):
        User.objects.create_user(
            email="another@example.com",
            password="pass1234",
            document=self.valid_payload["document"],
        )
        response = self.client.post(self.url, self.valid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("document", response.data)
