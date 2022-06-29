from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from comments.api.permissions import IsObjectOwner
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):
    """
    only need list, create, update, destroy
    do not need to retrieve a single comment.
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['destroy', 'update']:
            # return 2 value because we want to know
            # the detailed information when the request is denied
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # 有required_params就可以不用写下面这部分了
        # if 'tweet_id' not in request.query_params:
        #     return Response({
        #         'message': 'missing tweet_id in request',
        #         'success': False,
        #     }, status=status.HTTP_400_BAD_REQUEST,)
        # Another approach:
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id)
        queryset = self.get_queryset() # get_queryset() can be overridden
        # 使用prefetch related可以进行优化
        comments = self.filter_queryset(queryset).prefetch_related('user').order_by('created_at')
        serializer = CommentSerializer(
            comments,
            context={'request': request},
            many=True,
        )
        return Response({
            'comments': serializer.data,
        }, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }

        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # .save() will trigger the create method in serializer.
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )
    # similar to create
    def update(self, request, *args, **kwargs):
        # get_object is a function in django rest framework.
        # It will raise 404 error when cannot find the object.
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data,
        )

        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # The .save() will trigger the update method in serializer.
        # .save() will judge whether to use create or update based on the argument of instance
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        # 真删除？
        comment.delete()
        # the default return value of destroy is status code 204 no content
        # Here we return success = True to make it more understandable
        return Response({
            'success': True,
        }, status=status.HTTP_200_OK)

