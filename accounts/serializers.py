from rest_framework import serializers
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



class UserProfileSerializer(serializers.ModelSerializer):
    """
    This serializer is for returning and updating an user
    """

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'last_login',)
        write_only_fields = ('password',)
        read_only_fields = ('date_joined', 'last_login',)

    def restore_object(self, attrs, instance=None):
        # call set_password on user object. Without this
        # the password will be stored in plain text.
        user = super(UserProfileSerializer, self).restore_object(attrs, instance)
        user.set_password(attrs['password'])
        return user
