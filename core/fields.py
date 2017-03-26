from rest_framework.fields import Field


class TimezoneField(Field):
    """
    Take the timezone object and make it JSON serializable
    """
    def to_representation(self, obj):
        return obj.zone

    def to_internal_value(self, data):
        return data

