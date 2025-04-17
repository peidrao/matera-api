from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .usescases.get_account_use_case import GetAccountMeUseCase

from .serializers import MeSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = GetAccountMeUseCase().handle(request.user)
        serializer = MeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
