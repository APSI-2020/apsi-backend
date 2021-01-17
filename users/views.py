from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseBadRequest
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, UserGroupSerializer, LecturerSerializer
from .users_repository import LecturerRepository
from .users_repository import UsersGroupRepository
from .users_service import UsersService


class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)
    users_group_repository = UsersGroupRepository()

    @swagger_auto_schema(request_body=UserSerializer, operation_description='Endpoint for user registration.')
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        try:
            guest_user_group = self.users_group_repository.find_guest_user_group_or_fail()
        except ObjectDoesNotExist:
            return JsonResponse(dict(error_message='Guest user group not found.'),
                                safe=False,
                                status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if serializer.is_valid():
            try:
                user = serializer.save()
                user.groups.add(guest_user_group)
            except IntegrityError:
                return JsonResponse(dict(error_message='User with given email already exist.'),
                                    safe=False,
                                    status=status.HTTP_400_BAD_REQUEST)

            if user:
                json = serializer.data
                json['id'] = user.id
                return Response(json, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    users_service = UsersService()

    def get(self, request):
        token = get_authorization_header(request).decode('utf-8')

        user = self.users_service.fetch_by_jwt(token)

        serializer = UserSerializer(user)

        json = serializer.data

        return Response(json, status=status.HTTP_200_OK)


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


class LecturersView(APIView):
    lecturers_repository = LecturerRepository()
    users_service = UsersService()

    lecturers_response = openapi.Response('Return a list of all lecturers', LecturerSerializer(many=True))
    authorization_token = openapi.Parameter('Authorization', openapi.IN_HEADER,
                                            description="Authorization token which starts with Bearer",
                                            type=openapi.TYPE_STRING)

    @swagger_auto_schema(operation_description='Endpoint for retrieving all lecturers.',
                         responses={200: lecturers_response, 404: [], 403: []},
                         manual_parameters=[authorization_token])
    def get(self, request):
        jwt = request.headers['Authorization']
        user = self.users_service.fetch_by_jwt(jwt)

        if not user:
            return JsonResponse(data=None, status=status.HTTP_403_FORBIDDEN, safe=False)

        lecturers = self.lecturers_repository.get_all_lecturers()

        if not lecturers:
            return JsonResponse(data=[], status=status.HTTP_404_NOT_FOUND, safe=False)

        serializer = LecturerSerializer(lecturers, many=True)
        response = serializer.data
        return JsonResponse(response, safe=False)
