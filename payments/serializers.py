from rest_framework import serializers

from .models import Payments


class CreatePaymentSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField()

    class Meta:
        model = Payments
        fields = ('event_id',)

    def create(self, validated_data):
        instance = self.Meta.model(
            price=self.context['price'], user=self.context['user'], event=self.context['event'])

        return instance


class PaymentURLSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    price = serializers.FloatField()
    url = serializers.SerializerMethodField('get_payment_url')

    class Meta:
        fields = ('event_id', 'url', 'price')

    def get_payment_url(self, data_dict):
        return "https://pl.wikipedia.org/wiki/Autostopem_przez_Galaktyk%C4%99"
