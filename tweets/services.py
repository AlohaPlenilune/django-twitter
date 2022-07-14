from tweets.models import TweetPhoto, Tweet
from twitter.cache import USER_TWEETS_PATTERN
from utils.redis_helper import RedisHelper


'''
currently we do not support editing tweet. So the tweet cache does not have to handle with
the situation that tweet is edited.
'''

class TweetService(object):

    @classmethod
    def create_photos_from_files(cls, tweet, files):
        photos = []
        for index, file in enumerate(files):
            photo = TweetPhoto(
                tweet=tweet,
                user=tweet.user,
                file=file,
                order=index,
            )
            photos.append(photo)
        TweetPhoto.objects.bulk_create(photos)


    @classmethod
    def get_cached_tweets(cls, user_id):
        # queryset is lazy loading, so won't visit the database here
        queryset = Tweet.objects.filter(user_id=user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=user_id)
        # 在load_objects中如果没有这个tweet的cache，才会访问数据库得到queryset的结果
        return  RedisHelper.load_objects(key, queryset)

    # use this when creating tweet (listener)
    @classmethod
    def push_tweet_to_cache(cls, tweet):
        queryset = Tweet.objects.filter(user_id=tweet.user_id).order_by('-created_at')
        key = USER_TWEETS_PATTERN.format(user_id=tweet.user_id)
        RedisHelper.push_object(key, tweet, queryset)
