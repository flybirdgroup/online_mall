from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ImportPaginationclass(PageNumberPagination):
    # Client can control the page using this query parameter.
    page_query_param = 'page'

    # Client can control the page size using this query parameter.
    # Default is 'None'. Set to eg 'page_size' to enable usage.
    page_size_query_param = 'pagesize'

    # Set to an integer to limit the maximum page size the client may request.
    # Only relevant if 'page_size_query_param' has also been set.
    max_page_size = 5

    last_page_strings = ('last',)

    template = 'rest_framework/pagination/numbers.html'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('pages', self.page.paginator.num_pages),
            ('page', self.page.number),
            ("pagesize", self.page_size),
            ('lists', data)
        ]))