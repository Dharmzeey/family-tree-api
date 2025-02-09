from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    page_size = 30  # Default page size
    page_size_query_param = 'page_size'  # Allow client to override the page size
    max_page_size = 100  # Maximum page size
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response({
            "data": data,  # Replace "results" with "data"
            "pagination": {
                "total": self.page.paginator.count,
                "page": self.page.number,
                "page_size": self.get_page_size(self.request),
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            }
        })
    