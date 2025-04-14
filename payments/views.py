from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
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
        loan = serializer.validated_data["loan"]

        if loan.user != request.user:
            return Response(
                {"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN
            )

        payment = serializer.save()

        if loan.is_fully_paid:
            return Response(
                {"detail": "Este empréstimo já foi quitado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_paid = loan.total_paid
        total_due = loan.outstanding_balance + total_paid

        if total_paid >= total_due:
            loan.is_fully_paid = True
            loan.save(update_fields=["is_fully_paid"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)
