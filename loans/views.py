from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Loan
from .serializers import LoanSerializer


class LoanViewSet(viewsets.ModelViewSet):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Loan.objects.filter(user=self.request.user)
            .select_related("user")
            .order_by("-created_at")
        )

    @transaction.atomic
    def perform_create(self, serializer):
        ip = self.request.META.get("REMOTE_ADDR", "127.0.0.1")
        serializer.save(user=self.request.user, ip_address=ip)
