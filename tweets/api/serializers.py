from rest_framework import serializers

from comments.api.serializers import CommentSerializer
from tweets.models import Tweet
from accounts.api.serializers import UserSerializer, UserSerializerForTweet


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForTweet() # get detailed user information rather than just user_id

    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content')

class TweetSerializerWithComments(TweetSerializer):
    user = UserSerializer()
    comments = CommentSerializer(source='comment_set', many=True)
    # TODO 用serializers.SerializerMethodField 实现comments，如下
    # def get_comments(self, obj):
    #    return CommentSerializer(obj.comment_set.all(), many=True).data
    class Meta:
        model = Tweet
        fields = ('id', 'user', 'created_at', 'content', 'comments')



class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length=6, max_length=140)
    class Meta:
        model = Tweet
        fields = ('content',) # should not include user_id and so on.

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet
