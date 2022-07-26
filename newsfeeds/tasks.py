from celery import shared_task

from friendships.services import FriendshipService
from newsfeeds.constants import FANOUT_BATCH_SIZE
from newsfeeds.models import NewsFeed
from tweets.models import Tweet
from utils.time_constants import ONE_HOUR

# we need tweet_id and follower_id to create newsfeed.
# So directly pass in both of them can reduce one db query
@shared_task(routing_key='newsfeeds', time_limit=ONE_HOUR)
def fanout_newsfeeds_batch_task(tweet_id, follower_ids):
    # this is not the final version of this function. will improve it later
    # import inside the function to avoid circle dependency
    from newsfeeds.services import NewsFeedService

    # shouldn't use sql query inside for loop!
    # for follower_id in follower_ids:
    #     NewsFeed.objects.create(user_id=follower_id, tweet_id=tweet_id)

    # correct approach: use bulk_create
    newsfeeds = [
        NewsFeed(user_id=follower_id, tweet_id=tweet_id)
        for follower_id in follower_ids
    ]
    NewsFeed.objects.bulk_create(newsfeeds)

    # bulk create will not trigger post_save signal, so we need to manually push into cache
    for newsfeed in newsfeeds:
        NewsFeedService.push_newsfeed_to_cache(newsfeed)

    # async can have return value, which will show in the log
    return "{} newsfeeds created.".format(len(newsfeeds))

@shared_task(routing_key='default', time_limit=ONE_HOUR)
def fanout_newsfeeds_main_task(tweet_id, tweet_user_id):
    # first create the newsfeed that fanout to oneself, so that the author can see the tweet right now.
    NewsFeed.objects.create(user_id=tweet_user_id, tweet_id=tweet_id)

    # get all follower ids, divide them based on the batch size
    follower_ids = FriendshipService.get_follower_ids(tweet_user_id)
    index = 0
    while index < len(follower_ids):
        batch_ids = follower_ids[index: index + FANOUT_BATCH_SIZE]
        fanout_newsfeeds_batch_task.delay(tweet_id, batch_ids)
        index += FANOUT_BATCH_SIZE
    return "{} newsfeeds going to fanout, {} batches created.".format(
        len(follower_ids),
        (len(follower_ids) - 1) // FANOUT_BATCH_SIZE + 1,
    )
