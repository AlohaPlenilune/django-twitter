from datetime import timedelta
from testing.testcases import TestCase
from utils.time_helpers import utc_now

# Create your tests here.


class TweetTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user(username='user1')
        self.tweet = self.create_tweet(user=self.user1, content='meow')
        self.user2 = self.create_user(username='user2')

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10) # hours_to_now is a property

    def test_like_set(self):
        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user1, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        self.create_like(self.user2, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)