
# should end with '/', otherwise will cause 301 redirect
from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase
from tweets.models import Tweet

TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'


class TweetApiTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1', 'user1@example.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2', 'user2@example.com')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    def test_list_api(self):
        # test if not have user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        # normal request
        response = self.anonymous_client.get(
            TWEET_LIST_API,
            data={'user_id':self.user1.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 3)

        response = self.anonymous_client.get(
            TWEET_LIST_API,
            data={'user_id': self.user2.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tweets']), 2)

        # Test if the new created is behind the previous one.
        self.assertEqual(response.data['tweets'][0]['id'], self.tweets2[1].id)
        self.assertEqual(response.data['tweets'][1]['id'], self.tweets2[0].id)

    def test_create_api(self):
        # Test if not logged in
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)

        # Test if post no content
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)

        # Test if the content is too short
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)

        # Test if the content is too long
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '0' * 141})
        self.assertEqual(response.status_code, 400)

        # Test normal post
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(
            TWEET_CREATE_API,
            {'content': 'This is a testing tweet!'},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve(self):
        # test retrieve non-existed tweet id
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # test will show comments when retrieving a tweet
        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        # print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.user2, tweet, '1')
        self.create_comment(self.user1, tweet, '2')
        # make sure the returned count of comments only include a specific tweet
        self.create_comment(self.user1, self.create_tweet(self.user2), '3')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)

        # tweet 里包含用户的头像和昵称
        profile = self.user1.profile
        self.assertEqual(response.data['user']['nickname'], profile.nickname)
        self.assertEqual(response.data['user']['avatar_url'], None)

