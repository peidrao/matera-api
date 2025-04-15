from rest_framework import serializers

from loans.models import Loan


class LoanSerializer(serializers.ModelSerializer):
    outstanding_balance = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    compounded_amount = serializers.SerializerMethodField()
    iof = serializers.SerializerMethodField()
    insurance = serializers.SerializerMethodField()
    total_due = serializers.SerializerMethodField()

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
            "compounded_amount",
            "iof",
            "insurance",
            "total_due",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "requested_date",
            "ip_address",
            "outstanding_balance",
            "total_paid",
            "compounded_amount",
            "iof",
            "insurance",
            "total_due",
            "created_at",
            "updated_at",
        ]

    def get_outstanding_balance(self, obj):
        return round(obj.outstanding_balance, 2)

    def get_total_paid(self, obj):
        return round(obj.total_paid, 2)

    def get_compounded_amount(self, obj):
        return round(obj.compounded_amount, 2)

    def get_iof(self, obj):
        return round(obj.iof, 2)

    def get_insurance(self, obj):
        return round(obj.insurance, 2)

    def get_total_due(self, obj):
        return round(obj.total_due, 2)
