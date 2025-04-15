from rest_framework import serializers

from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "loan", "payment_date", "amount"]
        read_only_fields = ["id", "payment_date"]
