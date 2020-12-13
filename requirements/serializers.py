from rest_framework import serializers


class StringListField(serializers.ListField):
    child = serializers.CharField()


class CreateRequirementsSerializer(serializers.Serializer):
    type = serializers.CharField()
    groups = StringListField()

    class Meta:
        fields = ['type', 'groups']
