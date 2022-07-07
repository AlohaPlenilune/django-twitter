from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class FriendshipPagination(PageNumberPagination):
    # the default page size, if the page size parameter is not in the url
    page_size = 20
    # The default page_size_query_param is None, which means
    # the client cannot choose the page size
    # if we include this param, it means the client can assign a size
    # eg. mobile and web visit a same API but need different page size
    page_size_query_param = 'size'
    # The largest size that allowed
    max_page_size = 20

    # 完成翻页返回给前端的数据
    def get_paginated_response(self, data):
        return Response({
            'total_results': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'has_next_page': self.page.has_next(),
            'results': data, # the previous followings and followers are all results
        })