from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from accounts.api.serializers import UserSerializer, UserSerializerForLike
from comments.models import Comment
from likes.models import Like
from tweets.models import Tweet

class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike(source='cached_user')

    class Meta:
        model = Like
        fields = ('user', 'created_at')

class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    content_type = serializers.ChoiceField(choices=['comment', 'tweet'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id')

    def _get_model_class(self, data):
        if data['content_type'] == 'comment':
            return Comment
        if data['content_type'] == 'tweet':
            return Tweet
        return None

    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError({
                'content_type': 'Content type does not exist',
            })
        # 不加first的话可能在这一步就会报错，而且是500类型错误，我们希望在下面报错，而且是400错误
        """first() returns the first object of a query or None if no match is found."""
        liked_object = model_class.objects.filter(id=data['object_id']).first()
        if liked_object is None:
            raise ValidationError({
                'object_id': 'Object does not exist',
            })
        return data

class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):
    def get_or_create(self):
        model_class = self._get_model_class(self.validated_data)
        instance = Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['request'].user,
        )
        return instance


class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):
    def cancel(self):
        """
        The cancel method is a user-defined method. cancel won't be called by serializer.save()
        So we should call it with serializer.cancel()
        """
        model_class = self._get_model_class(self.validated_data)
        # if not like item fit the filter requirements,
        deleted, _ = Like.objects.filter(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['request'].user,
        ).delete()
        return deleted # 1 or 0, not True or False
