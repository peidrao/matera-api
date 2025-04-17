from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import views, status

from .usescases.get_account_use_case import GetAccountMeUseCase

from .serializers import MeSerializer, RegisterSerializer


class RegisterView(views.APIView):
    permission_classes = []

    @extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
        description="Cria um novo usuário com e-mail, senha e documento.",
        summary="Registrar novo usuário",
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeView(views.APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: MeSerializer},
        description="Retorna o resumo financeiro do usuário autenticado.",
        summary="Obter dados da conta atual",
    )
    def get(self, request):
        data = GetAccountMeUseCase().handle(request.user)
        serializer = MeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
