import requests
from django.contrib.auth.base_user import BaseUserManager
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apsi.settings import BACKEND_URL, FRONTEND_URL, SSO_URL
from sso.models import SignedUsers
from users.models import Users
from users.serializers import UserSerializer
from users.users_service import UsersServiceException, UsersService


class SingleSignOn(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        urls = dict(redirectUrl=FRONTEND_URL + "/auth", webhookUrl=BACKEND_URL + "/api/sso/confirm/")
        response = requests.post(SSO_URL + "/session/create/", json=urls)
        session_id = response.json()['id']
        return JsonResponse(dict(redirectUrl=SSO_URL + f'/session/{session_id}'))


class SingleSignOnConfirm(APIView):
    users_service = UsersService()
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data_from_sso = request.data
        sso_id = data_from_sso['user']['id']
        access_token = data_from_sso['access_token']

        if SignedUsers.objects.filter(sso_id=sso_id).count() == 0:
            sso_user = request.data['user']
            password = BaseUserManager().make_random_password(45)
            sso_user['id'] = None
            sso_user['password'] = password
            sso_user['confirm_password'] = password
            serializer = UserSerializer(data=sso_user)
            try:
                response = self.users_service.create_user(user_serializer=serializer)
            except UsersServiceException as e:
                return e.response
            created_user = response.json
            user = Users.objects.filter(pk=created_user['id']).get()
            SignedUsers.objects.create(sso_id=sso_id, user=user, access_token=access_token)
        else:
            SignedUsers.objects.filter(sso_id=sso_id).update(access_token=access_token)

        return HttpResponse()


class SingleSignOnLogIn(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        if SignedUsers.objects.filter(access_token=request.data['access_token']).count() == 0:
            return HttpResponseBadRequest()
        else:
            sso_user = SignedUsers.objects.filter(access_token=request.data['access_token']).get()
            user = sso_user.user
            refresh = RefreshToken.for_user(user)

            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
