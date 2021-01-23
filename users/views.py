from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, UserGroupSerializer, LecturerSerializer
from .users_repository import LecturerRepository
from .users_repository import UsersGroupRepository
from .users_service import UsersService, UsersServiceException


class UserCreate(APIView):
    permission_classes = (permissions.AllowAny,)
    users_service = UsersService()

    @swagger_auto_schema(request_body=UserSerializer, operation_description='Endpoint for user registration.')
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        try:
            return self.users_service.create_user(user_serializer=serializer).response
        except UsersServiceException as e:
            return e.response


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

    name = openapi.Parameter('name', openapi.IN_QUERY,
                             description="Returns user groups with name containg given string",
                             type=openapi.TYPE_STRING)

    user_groups_response = openapi.Response('response description', UserGroupSerializer(many=True))

    @swagger_auto_schema(operation_description='Endpoint for retrieving all users groups.',
                         manual_parameters=[name],
                         responses={200: user_groups_response, 404: []})
    def get(self, request):

        parameters = dict(request.GET)
        name = parameters.get('name', None)

        if name is None:
            users_groups = UsersGroupRepository.get_all_users_groups()
        else:
            name = name[0]  # it is always returned as list
            users_groups = UsersGroupRepository.get_users_groups_with_name_containing(name)

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
