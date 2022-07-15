from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerForDetail,
)
from tweets.models import Tweet
from newsfeeds.services import NewsFeedService
from tweets.services import TweetService
from utils.decorators import required_params
from utils.paginations import EndlessPagination


class TweetViewSet(viewsets.GenericViewSet):
    # 'TweetViewSet' should either include a `serializer_class` attribute,
    # or override the `get_serializer_class()` method.
    # attention!!! do not use TweetSerializer otherwise need to input user_name manually
    serializer_class = TweetSerializerForCreate
    # 这里不声明queryset的话retrieve里面的get_objects()并不知道去哪里get
    queryset = Tweet.objects.all()
    pagination_class = EndlessPagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @required_params(params=['user_id']) # if not include 'use_id', return 400
    def list(self, request):
        # 因为有了required_params检测，所以下面这部分可以省略掉
        # if 'user_id' not in request.query_params:
        #     return Response('missing user_id', status=400)
        user_id = request.query_params['user_id']
        tweets = TweetService.get_cached_tweets(user_id=user_id)
        tweets = self.paginate_queryset(tweets)
        serializer = TweetSerializer(
            tweets,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # TODO 通过某个query参数with_all_comments来决定是否需要带上所有comments
        # TODO 通过某个query参数with_preview_comments来决定是否需要带上前三条comments
        tweet = self.get_object() # will raise 404 if no object
        serializer = TweetSerializerForDetail(
            tweet,
            context={'request': request},
        )
        return Response(serializer.data)

    def create(self, request):
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request': request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input.',
                'errors': serializer.errors,
            }, status=400)
        # save will trigger create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        # use TweetSerializerForCreate when creating tweet, use TweetSerializer when showing the tweet
        return Response(
            TweetSerializer(tweet, context={'request': request}).data,
            status=201,
        )