from rest_framework import serializers
from loans.models import Loan


class LoanSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()

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

    def get_outstanding_balance(self, obj):
        return round(obj.outstanding_balance, 2)

    def get_total_paid(self, obj):
        return round(obj.total_paid, 2)
