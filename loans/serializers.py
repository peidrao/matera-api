from rest_framework import serializers
from loans.models import Loan


class LoanSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.DecimalField(
        source="outstanding_balance", max_digits=12, decimal_places=2, read_only=True
    )
    total_paid = serializers.DecimalField(
        source="total_paid", max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = Loan
        fields = [
            "id",
            "principal_amount",
            "monthly_interest_rate",
            "ip_address",
            "requested_date",
            "bank",
            "client",
            "outstanding_balance",
            "total_paid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requested_date",
            "ip_address",
            "outstanding_balance",
            "total_paid",
            "created_at",
            "updated_at",
        ]
