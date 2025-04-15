from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from loans.models import Loan
from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(loan__user=self.request.user).select_related(
            "loan"
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        loan_id = serializer.validated_data["loan"].id

        loan = (
            Loan.objects.select_for_update()
            .select_related("user")
            .get(
                id=loan_id,
            )
        )

        if loan.user != request.user:
            return Response(
                {"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN
            )

        if loan.is_fully_paid:
            return Response(
                {"detail": "Este empréstimo já foi quitado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_paid = loan.payments.aggregate(total=Sum("amount"))["total"] or Decimal(
            "0.00"
        )
        total_due = loan.total_due
        new_amount = serializer.validated_data["amount"]

        if total_paid + new_amount > total_due:
            return Response(
                {"detail": "O valor excede o saldo devedor."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        if total_paid + new_amount >= total_due:
            loan.is_fully_paid = True
            loan.save(update_fields=["is_fully_paid"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)
