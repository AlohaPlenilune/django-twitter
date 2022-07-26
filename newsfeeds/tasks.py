from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR


@shared_task(time_limit=ONE_HOUR)
def fanout_newsfeeds_task(tweet_id):
    # this is not the final version of this function. will improve it later
    # import inside the function to avoid circle dependency
    from newsfeeds.services import NewsFeedService

    # shouldn't use sql query inside for loop!
    # for follower in FriendshipService.get_followers(tweet.user):
    #     NewsFeed.objects.create(
    #         user=follower,
    #         tweet=tweet,
    #     )

    # correct approach: use bulk_create
    tweet = Tweet.objects.get(id=tweet_id)
    newsfeeds = [
        NewsFeed(user=follower, tweet=tweet)
        for follower in FriendshipService.get_followers(tweet.user)
    ]
    newsfeeds.append(NewsFeed(user=tweet.user, tweet=tweet))
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk create will not trigger post_save signal, so we need to manually push into cache
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    # async can have return value, which will show in the log
    # return ...

