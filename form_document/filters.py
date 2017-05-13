from django_filters import Filter
from django_filters.fields import Lookup


class StatusFilter(Filter):
    def filter(self, qs, value):
        value_list = value.split(u',')
        return super(StatusFilter, self).filter(qs, Lookup(value_list, 'in'))
