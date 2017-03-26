from rest_framework import serializers

from core.fields import TimezoneField
from accounts.models import User
import uuid


class PaidSignupFormSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField()
    credit_card_number = serializers.CharField()
    credit_card_expiry = serializers.CharField()
    credit_card_cvc = serializers.CharField()
    plan_id = serializers.CharField()
    number_of_user = serializers.IntegerField()

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


class FreeAccountCreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('date_joined', 'last_login',)

    def validate_email(self, value):
        """
        checking the email address has not already been used by another account
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email address already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username='user_%s' % uuid.uuid4().hex[:12],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=True  # todo: Set this to false once the account verification feature is done
        )
        return user



class UserProfileSerializer(serializers.ModelSerializer):
    """
    This serializer is for returning and updating an user
    """
    timezone = TimezoneField(required=False)
    old_password = serializers.CharField(required=False, write_only=True)
    new_password1 = serializers.CharField(required=False, write_only=True)
    new_password2 = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'last_login',
            'avatar',
            'timezone',
            'old_password',
            'new_password1',
            'new_password2',
        )
        read_only_fields = ('last_login', 'email',)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'new_password1':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance