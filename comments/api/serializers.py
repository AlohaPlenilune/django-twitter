from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from likes.services import LikeService
from tweets.models import Tweet


class CommentSerializer(serializers.ModelSerializer):
    # without user = UserSerializer(), the user in the fields will only be user_id,
    # rather than user information as UserSerializer defined.
    user = UserSerializerForComment(source='cached_user')
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'likes_count',
            'has_liked',
        )
    def get_likes_count(self, obj):
        return obj.like_set.count()
    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)

class CommentSerializerForCreate(serializers.ModelSerializer):
    # The default ModelSerializer only contains user and tweet rather than user_id and tweet_id
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = ('content', 'tweet_id', 'user_id')

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({'message': 'tweet does not exist'})
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )

# It's better to use seperated serializers for create and for update
class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        # user can only update content，so the fields only include content
        fields = ('content',)

    def update(self, instance, validated_data):
        # 使用了update，但实际上是partial update
        instance.content = validated_data['content']
        instance.save()
        # update method requires the changed instance as return value.
        return instance
