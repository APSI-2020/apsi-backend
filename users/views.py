from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseBadRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, UserGroupSerializer
from .users_repository import UsersGroupRepository
from .users_service import UsersService


class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)

    @swagger_auto_schema(request_body=UserSerializer, operation_description='Endpoint for user registration.')
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
            except IntegrityError:
                return HttpResponseBadRequest('User with given email already exist.')
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


class UserGroupsView(APIView):
    permission_classes = (permissions.AllowAny,)

    user_groups_response = openapi.Response('response description', UserGroupSerializer(many=True))

    @swagger_auto_schema(operation_description='Endpoint for retrieving all users groups.',
                         responses={200: user_groups_response, 404: []})
    def get(self, request):
        users_groups = UsersGroupRepository.get_all_users_groups()
        if users_groups:
            serializer = UserGroupSerializer(users_groups, many=True)
            response = serializer.data
            return JsonResponse(response, safe=False)
        else:
            return JsonResponse(data=[], status=status.HTTP_404_NOT_FOUND, safe=False)
