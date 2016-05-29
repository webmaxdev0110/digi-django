from collections import OrderedDict
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CorePagination(PageNumberPagination):
    '''
    Only provides pagination when the ``page_size`` querystring parameter
    is provided.
    '''
    
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        # Only difference to superclass is that we use the key name
        # `data` instead of `results`.
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('data', data)
        ]))


def get_pagination_class(page_size=None):
    """
    Returns a new pagination class with the given page size

    :param page_size: Page size of the pagination class
    :return: A pagination class derived from CanJSPagination
    """

    class PaginationClass(CorePagination):
        pass

    PaginationClass.page_size = page_size
    return PaginationClass
