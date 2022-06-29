from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from comments.models import Comment
from testing.testcases import TestCase

# any api that uses comments api should be tested.
COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'
TWEET_LIST_API = '/api/tweets/'
TWEET_DETAIL_API = '/api/tweets/{}/'
NEWSFEED_LIST_API = '/api/newsfeeds/'


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

    def test_destroy(self):
        comment = self.create_comment(self.user2, self.tweet)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # Cannot delete anonymously
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Can not delete the comment if not the author of the comment
        response = self.user1_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # The author of the comment can delete it
        # 这是所有comment的数量还是这条tweet的评论的数量？
        count = Comment.objects.count()
        response = self.user2_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.user2, self.tweet, 'original content')
        another_tweet = self.create_tweet(self.user1)
        url = '{}{}/'.format(COMMENT_URL, comment.id)

        # Cannot update anonymously
        response = self.anonymous_client.put(url, {'content': 'edited'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cannot update if not the author of the comment
        response = self.user1_client.put(url, {'content': 'edited'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'edited')

        # cannot update things other than content and updated time.
        before_updated_at = comment.updated_at
        before_created_at = comment.created_at
        now = timezone.now()
        response = self.user2_client.put(url, {
            'content': 'edited',
            'user_id': self.user1.id,
            'tweet_id': another_tweet.id,
            'created_at': now,
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'edited')
        self.assertEqual(comment.user, self.user2)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_created_at)
        #self.assertEqual(comment.updated_at, now)
        self.assertNotEqual(comment.updated_at, before_updated_at)

    def test_list(self):
        # test without tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # successfully visit with tweet_id
        # no comment at first
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['comments']), 0)

        # comments should be sorted in timeseries
        self.create_comment(self.user1, self.tweet, '1')
        self.create_comment(self.user2, self.tweet, '2')
        self.create_comment(self.user2, self.create_tweet(self.user2), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })

        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.user2.id,
        })
        self.assertEqual(len(response.data['comments']), 2)

    def test_comments_count(self):
        # test tweet detail api
        tweet = self.create_tweet(self.user1)
        url = TWEET_DETAIL_API.format(tweet.id)
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['comments_count'], 0)

        # test tweet list api
        self.create_comment(self.user1, tweet)
        response = self.user2_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['tweets'][0]['comments_count'], 1)

        # test newsfeeds list api
        self.create_comment(self.user2, tweet)
        self.create_newsfeed(self.user2, tweet)
        response = self.user2_client.get(NEWSFEED_LIST_API)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['comments_count'], 2)








