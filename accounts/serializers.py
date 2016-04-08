from django.db import transaction
from rest_framework import serializers
from accounts.models import User
import uuid


class OnboardingSignupFormSerializer(serializers.Serializer):
    full_name = serializers.CharField(write_only=True)
    email = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        full_name = validated_data['full_name'].strip()
        first_name = ''
        last_name = ''
        if ' ' in full_name:
            first_name = full_name.split(' ')[0]
            last_name = full_name.split(' ')[1]
        else:
            first_name = full_name

        user = User.objects.create_user(
            username='user_%s' % uuid.uuid4().hex[:8],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
        )
        return user

    def validate(self, attrs):
        return attrs
