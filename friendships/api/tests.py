from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from rest_framework import status


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'

class FriendshipApiTests(TestCase):
    def setUp(self):
        self.user1 = self.create_user('user1')
        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2')
        self.user2_client = APIClient()
        self.user2_client.force_authenticate(self.user2)

        # create followings and followers for user2
        for i in range(2):
            follower = self.create_user('user2_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.user2)
        for i in range(3):
            following = self.create_user('user2_following{}'.format(i))
            Friendship.objects.create(from_user=self.user2, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.user1.id)

        # test follow without login
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # test if use get
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, 405)

        # test follow oneself
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, 400)

        # followed successfully
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 201)

        # followed repeated successfully
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['duplicate'], True)

        # test if new data will is created if one follows his follower
        count = Friendship.objects.count()
        response = self.user1_client.post(FOLLOW_URL.format(self.user2.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.user1.id)

        # test unfollow without logging in
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # test unfollow with get
        response = self.user2_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test unfollow oneself
        response = self.user1_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # successfully unfollow
        Friendship.objects.create(from_user=self.user2, to_user=self.user1)
        count = Friendship.objects.count()
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # keep silence if unfollow before following.
        count = Friendship.objects.count()
        response = self.user2_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.user2.id)

        # test get followings with post
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test use get successfully
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['followings']), 3)

        # test if the list is in timeseries order
        timeseries0 = response.data['followings'][0]['created_at']
        timeseries1 = response.data['followings'][1]['created_at']
        timeseries2 = response.data['followings'][2]['created_at']
        self.assertEqual(timeseries0 > timeseries1, True)
        self.assertEqual(timeseries1 > timeseries2, True)
        self.assertEqual(
            response.data['followings'][0]['user']['username'],
            'user2_following2',
        )
        self.assertEqual(
            response.data['followings'][1]['user']['username'],
            'user2_following1',
        )
        self.assertEqual(
            response.data['followings'][2]['user']['username'],
            'user2_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.user2.id)
        # test if use post
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        #test if use get
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['followers']), 2)

        # test if the list is in timeseries order
        ts0 = response.data['followers'][0]['created_at']
        ts1 = response.data['followers'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['followers'][0]['user']['username'],
            'user2_follower1',
        )
        self.assertEqual(
            response.data['followers'][1]['user']['username'],
            'user2_follower0',
        )



