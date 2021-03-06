from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from ratelimit.decorators import ratelimit
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from django.contrib.auth import (
    authenticate as django_authenticate,
    login as django_login,
    logout as django_logout,
)
from accounts.api.serializers import (
    SignupSerializer,
    LoginSerializer,
    UserSerializer,
    UserProfileSerializerForUpdate,
    UserSerializerWithProfile,
)
from accounts.models import UserProfile
from utils.permissions import IsObjectOwner


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
     API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializerWithProfile
    # 因为能看所有用户的，不是什么用户都可以，必须是管理员
    permission_classes = (permissions.IsAdminUser,)

class AccountViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)
    serializer_class = SignupSerializer

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate = '3/s', method='POST', block=True))
    def signup(self, request):
        """
        Use username, email, password to sign up
        """
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)

        user = serializer.save()

        django_login(request, user)
        return Response({
            'success': True,
            'user': UserSerializer(user).data,
        }, status=201)


    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate = '3/s', method='POST', block=True))
    def login(self, request):
        """
         The default username is admin, password also is admin.
        """
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "message": "Please check input",
                "errors": serializer.errors,
            }, status=400)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                "success": False,
                "message": "username and password does not match",
            }, status=400)
        django_login(request, user)
        return Response({
            "success": True,
            "user": UserSerializer(instance=user).data,
        })

    @action(methods=['GET'], detail=False)
    @method_decorator(ratelimit(key='ip', rate = '3/s', method='GET', block=True))
    def login_status(self, request):
        """
         Check the current login status and detailed information.
        """
        data = {
            'has_logged_in': request.user.is_authenticated,
            'ip': request.META['REMOTE_ADDR'],
        }
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    @method_decorator(ratelimit(key='ip', rate = '3/s', method='POST', block=True))
    def logout(self, request):
        """
         登出当前⽤户
        """
        django_logout(request)
        return Response({"success": True})


class UserProfileViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.UpdateModelMixin,
):
    queryset = UserProfile
    permission_classes = (permissions.IsAuthenticated, IsObjectOwner,)
    serializer_class = UserProfileSerializerForUpdate