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
