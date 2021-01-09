from rest_framework import serializers

from .models import Payments


class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = ('timestamp', 'price')

    def create(self, validated_data):
        price = validated_data.pop('price')
        timestamp = validated_data.pop('timestamp')

        instance = self.Meta.model(
            price=price, timestamp=timestamp, user=self.context['user'], event=self.context['event'])

        return instance
