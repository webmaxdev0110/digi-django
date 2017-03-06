from rest_framework import serializers
from contacts.models import Person


class PersonSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'date_of_birth',
            'gender',
            'mobile_number',
        )
