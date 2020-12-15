from rest_framework import serializers

from requirements.requirements_checker import RequirementsChecker


class StringListField(serializers.ListField):
    child = serializers.CharField()


def is_a_proper_type(value):
    if value not in RequirementsChecker.ALL_TYPES:
        raise serializers.ValidationError(
            'Requirement type must be one of following values: ' + str(RequirementsChecker.ALL_TYPES))


class CreateRequirementsSerializer(serializers.Serializer):
    type = serializers.CharField(validators=[is_a_proper_type])
    groups = StringListField()

    class Meta:
        fields = ['type', 'groups']
