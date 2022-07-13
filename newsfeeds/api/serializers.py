from rest_framework import serializers
from newsfeeds.models import NewsFeed
from tweets.api.serializers import TweetSerializer

class NewsFeedSerializer(serializers.ModelSerializer):
    tweet = TweetSerializer(source='cached_tweet') # TweetSerializer() has already included UserSerializer()

    class Meta:
        model = NewsFeed
        fields = ('id', 'created_at', 'tweet')
