from rest_framework import serializers


class UserMeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    document = serializers.CharField()
    created_at = serializers.DateTimeField()


class LoanSummarySerializer(serializers.Serializer):
    total_loans = serializers.IntegerField()
    fully_paid_loans = serializers.IntegerField()
    active_loans = serializers.IntegerField()
    principal_amount_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    amount_paid_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    outstanding_balance_total = serializers.DecimalField(
        max_digits=12, decimal_places=2
    )
    percent_paid = serializers.DecimalField(max_digits=5, decimal_places=2)


class MeSerializer(serializers.Serializer):
    user = UserMeSerializer()
    loans = LoanSummarySerializer()


from rest_framework import serializers
from accounts.models import User


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    document = serializers.CharField(max_length=20)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("E-mail já está em uso.")
        return value

    def validate_document(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("O CPF/CNPJ deve conter apenas números.")
        if User.objects.filter(document=value).exists():
            raise serializers.ValidationError("Documento já está em uso.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
