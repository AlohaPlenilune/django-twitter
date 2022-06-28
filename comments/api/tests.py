from rest_framework import status
from rest_framework.test import APIClient

from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'

class CommentApiTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        self.tweet = self.create_tweet(self.user1)

    def test_create(self):
        # cannot create comment without logging in
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # cannot comment without any args
        response = self.user2_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # cannot comment without content
        response = self.user2_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # cannot comment without tweet_id
        response = self.user2_client.post(COMMENT_URL, {'content': 'test comment'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # cannot comment with too long content
        response = self.user2_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
             'content': '1' * 141,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('content' in response.data['errors'], True)

        # successfully with tweet_id & content within the range
        response = self.user2_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': 'test comment',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # if met problem, print the response.data to check the details
        # print(response.data)
        self.assertEqual(response.data['user']['id'], self.user2.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], 'test comment')


