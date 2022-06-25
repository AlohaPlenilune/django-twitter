from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from rest_framework import status


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'

class NewsFeedApiTest(TestCase):
    def setUp(self):

        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

    def test_list(self):
        # test without logging in
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test using post
        response = self.user1_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test shows nothing at first
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 0)

        # test that tweets posted by oneself can be seen.
        self.user1_client.post(POST_TWEETS_URL, {'content': 'user1 first tweet'})
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 1)

        # can see other's tweets after following
        self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        response = self.user2_client.post(POST_TWEETS_URL, {'content': 'user2 first tweet'})
        posted_tweet_id = response.data['id']
        response = self.user1_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)




