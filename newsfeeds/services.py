from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from newsfeeds.tasks import fanout_newsfeeds_task
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_helper import RedisHelper


class NewsFeedService(object):
    #service 中的方法大多是class method，不需要额外new instance
    @classmethod
    def fanout_to_followers(cls, tweet):
        # with delay means asynch
        fanout_newsfeeds_task.delay(tweet.id)
        # without delay means sync.
        # fanout_newsfeeds_task(tweet.id)
        # when doing unit tests, the 'delay' will be removed as we set in the settings.py

    # similar to get cached_tweets()
    @classmethod
    def get_cached_newsfeeds(cls, user_id):
        queryset = NewsFeed.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=user_id)
        return RedisHelper.load_objects(key, queryset)

    @classmethod
    def push_newsfeed_to_cache(cls, newsfeed):
        queryset = NewsFeed.objects.filter(user_id=newsfeed.user_id).order_by('-created_at')
        key = USER_NEWSFEEDS_PATTERN.format(user_id=newsfeed.user_id)
        RedisHelper.push_object(key, newsfeed, queryset)