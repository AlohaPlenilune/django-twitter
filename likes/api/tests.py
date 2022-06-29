from rest_framework import status

from testing.testcases import TestCase

LIKE_BASE_URL = '/api/likes/'

class LikeApiTest(TestCase):

    def setUp(self):
        self.user1, self.user1_client = self.create_user_and_client('user1')
        self.user2, self.user2_client = self.create_user_and_client('user2')

    def test_tweet_likes(self):
        tweet = self.create_tweet(self.user1)
        data = {
            'content_type': 'tweet',
            'object_id': tweet.id,
        }
        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get is not allowed
        response = self.user1_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # post successfully
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tweet.like_set.count(), 1)

        # cannot repeat like
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 1)
        response = self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(tweet.like_set.count(), 2)


    def test_comment_likes(self):
        tweet = self.create_tweet(self.user1)
        comment = self.create_comment(self.user2, tweet)
        data = {
            'content_type': 'comment',
            'object_id': comment.id,
        }

        # anonymous is not allowed
        response = self.anonymous_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # get is not allowed
        response = self.user1_client.get(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # wrong content type
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'comm',
            'object_id': comment.id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('content_type' in response.data['errors'], True)

        # wrong object_id
        response = self.user1_client.post(LIKE_BASE_URL, {
            'content_type': 'comment',
            'object_id': -1,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual('object_id' in response.data['errors'], True)

        #post success
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(comment.like_set.count(), 1)

        # repeat likes
        response = self.user1_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 1)
        response = self.user2_client.post(LIKE_BASE_URL, data)
        self.assertEqual(comment.like_set.count(), 2)








