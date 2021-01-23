import json

from rest_framework import serializers

from events.models import Events, Places
from payments.payments_repository import PaymentsRepository
from requirements.models import Requirements
from requirements.serializers import CreateRequirementsSerializer
from users.serializers import UserSerializer


def user_signed_up_for_event(event, user_id):
    users_ids = list(map(lambda participant: participant.pk, event.participants.all()))
    return user_id in users_ids


def user_is_lecturer_in_event(event, user_id):
    lecturers_ids = list(map(lambda lecturer: lecturer.pk, event.lecturers.all()))
    return user_id in lecturers_ids


def user_paid_for_event(user, event):
    payments = PaymentsRepository().get_payment_for_user_and_event(user, event).exists()
    return payments


class CreatePlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Places
        fields = ('name', 'address')


class PlaceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')

    class Meta:
        model = Places
        fields = ('id', 'name', 'address')


class CreateEventSerializer(serializers.ModelSerializer):
    requirements = CreateRequirementsSerializer(many=True, default=[])

    class Meta:
        model = Events
        fields = ('name', 'start', 'end', 'limit_of_participants', 'price', 'place', 'lecturers', 'requirements')

    def create(self, validated_data):
        requirements = validated_data.pop('requirements')
        saved_requirements = Requirements.objects.create(requirement_json=json.dumps(requirements))
        validated_data['requirements'] = saved_requirements
        lecturers = validated_data.pop('lecturers')
        instance = self.Meta.model(**validated_data)
        instance.save()
        instance.lecturers.add(*lecturers)
        return instance


class EventSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    is_signed_up_for = serializers.SerializerMethodField('get_signed_up_for')
    is_lecturer = serializers.SerializerMethodField('get_lecturer_in')
    amount_of_participants = serializers.IntegerField(source='number_of_participants')
    lecturers = UserSerializer(many=True)
    place = PlaceSerializer()
    payment_made = serializers.SerializerMethodField('get_user_payment_information', )

    def get_signed_up_for(self, event):
        return user_signed_up_for_event(event, self.context['user'].pk)

    def get_lecturer_in(self, event):
        return user_is_lecturer_in_event(event, self.context['user'].pk)

    def get_user_payment_information(self, event):
        return user_paid_for_event(self.context['user'], event)

    class Meta:
        model = Events
        fields = (
            'id', 'name', 'is_signed_up_for', 'is_lecturer', 'amount_of_participants', 'start', 'end',
            'limit_of_participants', 'price', 'payment_made', 'place', 'lecturers')
