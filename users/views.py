from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer
from .users_service import UsersService


class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=UserSerializer, operation_description='Endpoint for user registration.')
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                json = serializer.data
                return Response(json, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HelloWorldView(APIView):
    def get(self, request):
        us = UsersService()
        token = get_authorization_header(request).decode('utf-8')

        user = us.fetch_by_jwt(token)

        return Response(data={"hello": user.first_name}, status=status.HTTP_200_OK)
