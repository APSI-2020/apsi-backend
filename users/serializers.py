from django.db import IntegrityError
from django.http import HttpResponseBadRequest
from rest_framework import serializers

from .models import Users, UsersGroups


class UserSerializer(serializers.ModelSerializer):
    """
    Currently unused in preference of the below.
    """
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = Users
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)  # as long as the fields are the same, we can just use this
        if password is not None:
            instance.set_password(password)
        try:
            instance.save()
        except IntegrityError:
            return HttpResponseBadRequest('User with given email already exist.')

        return instance


class UserGroupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True)

    class Meta:
        model = UsersGroups
        fields = ('id', 'name')
