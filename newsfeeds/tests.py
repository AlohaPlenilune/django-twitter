from newsfeeds.models import NewsFeed
from newsfeeds.services import NewsFeedService
from newsfeeds.tasks import fanout_newsfeeds_main_task
from testing.testcases import TestCase
from twitter.cache import USER_NEWSFEEDS_PATTERN
from utils.redis_client import RedisClient


class NewsFeedServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('user2')

    def test_get_user_newsfeeds(self):
        newsfeed_ids = []
        for i in range(3):
            tweet = self.create_tweet(self.user2)
            newsfeed = self.create_newsfeed(self.user1, tweet)
            newsfeed_ids.append(newsfeed.id)
        newsfeed_ids = newsfeed_ids[::-1]

        # cache miss
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

        # cache hit
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

        # cache updated
        tweet = self.create_tweet(self.user1)
        new_newsfeed = self.create_newsfeed(self.user1, tweet)
        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1)
        newsfeed_ids.insert(0, new_newsfeed.id)
        self.assertEqual([f.id for f in newsfeeds], newsfeed_ids)

    def test_create_new_newsfeed_before_get_cached_newsfeed(self):
        newsfeed1 = self.create_newsfeed(self.user1, self.create_tweet(self.user1))

        RedisClient.clear()
        conn = RedisClient.get_connection()

        key = USER_NEWSFEEDS_PATTERN.format(user_id=self.user1.id)
        self.assertEqual(conn.exists(key), False)

        newsfeed2 = self.create_newsfeed(self.user1, self.create_tweet(self.user1))
        self.assertEqual(conn.exists(key), True)

        newsfeeds = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual([f.id for f in newsfeeds], [newsfeed2.id, newsfeed1.id])


class NewsFeedTaskTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.user1 = self.create_user('user1')
        self.user2 = self.create_user('uesr2')

    def test_fanout_main_task(self):
        tweet = self.create_tweet(self.user1, 'tweet1')
        self.create_friendship(self.user2, self.user1)
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, '1 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(1 + 1, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 1)

        for i in range(2):
            user = self.create_user('newuser{}'.format(i))
            self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet2')
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, '3 newsfeeds going to fanout, 1 batches created.')
        self.assertEqual(4 + 2, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 2)

        user = self.create_user('another user')
        self.create_friendship(user, self.user1)
        tweet = self.create_tweet(self.user1, 'tweet3')
        msg = fanout_newsfeeds_main_task(tweet.id, self.user1.id)
        self.assertEqual(msg, '4 newsfeeds going to fanout, 2 batches created.')
        self.assertEqual(5 + 6, NewsFeed.objects.count())
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user1.id)
        self.assertEqual(len(cached_list), 3)
        cached_list = NewsFeedService.get_cached_newsfeeds(self.user2.id)
        self.assertEqual(len(cached_list), 3)
