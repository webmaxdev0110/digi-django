from rest_framework import serializers


class EmailAddressVerificationSerializer(serializers.Serializer):
    result = serializers.BooleanField()
