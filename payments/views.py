from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .usecases import ProcessPaymentUseCase
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
        amount = serializer.validated_data["amount"]
        user = request.user

        payment = ProcessPaymentUseCase(
            loan=loan,
            user=user,
            amount=amount,
            ip_address=request.META.get("REMOTE_ADDR", "127.0.0.1"),
        ).handle()

        output_serializer = self.get_serializer(payment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
