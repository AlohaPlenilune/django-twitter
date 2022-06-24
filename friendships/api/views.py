from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from friendships.api.serializers import FollowerSerializer, FollowingSerializer
from friendships.models import Friendship


class FriendshipViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships(or users)/1/followers/
        # get all users whose to_user_id=pk, which means users who are following pk
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many=True)
        return Response({'followers': serializer.data}, status=200)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        serializer = FollowingSerializer(friendships, many=True)
        return Response({'followers': serializer.data}, status=200)

    def list(self, request):
        return Response({'message': 'This is friendships page.'})


