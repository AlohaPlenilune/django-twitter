from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from friendships.api.serializers import FollowerSerializer, FollowingSerializer, FriendshipSerializerForCreate
from friendships.models import Friendship
from utils.paginations import FriendshipPagination


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    # 通常来说，不同的views需要的pagination规则不同，因此一般需要分别定义
    pagination_class = FriendshipPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships(or users)/1/followers/
        # get all users whose to_user_id=pk, which means users who are following pk
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships) # get one page
        # 把这一页交给前端渲染
        serializer = FollowerSerializer(
            page,
            many=True,
            context={'request': request}
        )
        # 做这一层包装是考虑到paginator可能为空的情况（为空的话就什么都不做）
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        if Friendship.objects.filter(from_user=request.user, to_user=pk).exists():
            return Response({
                'message': 'You have already followed this person.',
                'duplicate': True,
            }, status=status.HTTP_201_CREATED)

        serializer = FriendshipSerializerForCreate(data={
            'from_user_id': request.user.id,
            'to_user_id': pk,
        })
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check the input.',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        return Response(
            # 凡是用FollowingSerializer和FollowerSerializer的都需要传context
            FollowingSerializer(instance, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()
        if request.user.id == unfollow_user.id: # pk is string format 1 != '1'
            return Response({
                'success': False,
                'message': 'You cannot unfollow yourself.',
            }, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = Friendship.objects.filter(
            from_user=request.user,
            to_user=unfollow_user,
        ).delete()
        return Response({'success': True, 'deleted': deleted})


    def list(self, request):
        return Response({'message': 'This is friendships page.'})


