from functools import wraps

from rest_framework import status
from rest_framework.response import Response


def required_params(method='GET', params=None):
    """
    when using @required_params(params=['some_param'],
    the required_params function should return a decorator function,
    the parameter of the decorator is the function view_func wrapped by @required_params
    """

    # 从效果上来说，参数中写params=[] 很多时候也没有太大问题
    # 但是从好的编程习惯上来说，函数的参数列表中的值不能是一个mutable的参数

    if params is None:
        params = []

    def decorator(view_func):
        """
        decorator function 通过 wraps 来将 view_fuc 里的参数解析出来传递给 ——wrapped_view
        这里的 instance 参数其实就是在view_func 里的self
        """
        @wraps(view_func)
        def _wrapped_view(instance, request, *args, **kwargs):
            if method.lower() == 'get':
                data = request.query_params
            else:
                data = request.data
            missing_params = [
                param for param in params
                if param not in data
            ]
            if missing_params:
                params_str = ','.join(missing_params)
                return Response({
                    'message': 'missing {} in request'.format(params_str),
                    'success': False,
                }, status=status.HTTP_400_BAD_REQUEST)
            return view_func(instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator
