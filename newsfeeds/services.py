from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed

class NewsFeedService(object):
    #service 中的方法大多是class method，不需要额外new instance
    @classmethod
    def fanout_to_followers(cls, tweet):
        # do not use for + query like following. The speed would be very slow!
        # for follower in followers:
        #     NewsFeed.objects.create(user=follower, tweet=tweet)
        newsfeeds = [
            NewsFeed(user=follower, tweet=tweet)
            for follower in FriendshipService.get_followers(tweet.user)
        ]
        newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
        # Attention: bulk_create is a keypoint method!!!
        NewsFeed.objects.bulk_create(newsfeeds)