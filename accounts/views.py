from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import MeSerializer
from .services import get_user_me


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = get_user_me(request.user)
        import pdb

        # pdb.set_trace()
        serializer = MeSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
