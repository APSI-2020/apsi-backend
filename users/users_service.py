from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import status

from .users_repository import UsersRepository, UsersGroupRepository
from django.conf import settings
import jwt


class UsersServiceException(Exception):
    def __init__(self, error):
        self.response = error


class UsersServiceResponse:
    def __init__(self, response, json):
        self.response = response
        self.json = json


class UsersService:
    def __init__(self):
        self.users_group_repository = UsersGroupRepository()
        self.user_repository = UsersRepository()

    def create_user(self, user_serializer, lecturer=False):
        guest_user_group = self.users_group_repository.find_guest_user_group_or_fail()
        lecturer_user_group = self.users_group_repository.find_lecturer_user_group_or_fail()

        if user_serializer.is_valid():
            try:
                user = user_serializer.save()
                if lecturer:
                    user.groups.add(lecturer_user_group)
                else:
                    user.groups.add(guest_user_group)
            except IntegrityError:
                error_response = JsonResponse(dict(error_message='User with given email already exist.'),
                                              safe=False,
                                              status=status.HTTP_400_BAD_REQUEST)
                raise UsersServiceException(error_response)

            if user:
                json = user_serializer.data
                json['id'] = user.id
                return UsersServiceResponse(response=JsonResponse(json, status=status.HTTP_201_CREATED), json=json)

        raise UsersServiceException(error=JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST))

    def fetch_by_jwt(self, token):
        token_begins_at = len(settings.SIMPLE_JWT['AUTH_HEADER_TYPES'][0]) + 1
        extracted_token = token[token_begins_at:]
        decoded = jwt.decode(extracted_token, settings.SECRET_KEY)
        user_id = decoded['user_id']

        return self.user_repository.find_by_id_or_fail(user_id)
