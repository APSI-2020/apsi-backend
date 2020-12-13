from rest_framework import serializers

from events.models import Events, Places
from users.models import Users
from users.serializers import UserSerializer


def user_signed_up_for_event(event, user_id):
    users_ids = list(map(lambda participant: participant.pk, event.participants.all()))
    return user_id in users_ids


class PlaceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')

    class Meta:
        model = Places
        fields = ('id', 'name', 'address')


class CreateEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Events
        fields = ('name', 'start', 'end', 'limit_of_participants', 'price', 'place', 'lecturers')


class EventSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk')
    is_signed_up_for = serializers.SerializerMethodField('get_signed_up_for')
    amount_of_participants = serializers.IntegerField(source='number_of_participants')
    lecturers = UserSerializer(many=True)
    place = PlaceSerializer()

    def get_signed_up_for(self, event):
        return user_signed_up_for_event(event, self.context['user'].pk)

    class Meta:
        model = Events
        fields = (
        'id', 'name', 'is_signed_up_for', 'amount_of_participants', 'start', 'end', 'limit_of_participants', 'price',
        'place', 'lecturers')
