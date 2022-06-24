from rest_framework import serializers

from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship


class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user') # source can be a field or method

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')


class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user') # source can be a field or method

    class Meta:
        model = Friendship
        fields = ('user', 'created_at')