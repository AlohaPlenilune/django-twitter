from friendships.models import Friendship
from friendships.services import FriendshipService
from testing.testcases import TestCase


class FriendshipServiceTests(TestCase):

    def setUp(self):
        self.clear_cache()
        self.lisa = self.create_user('lisa')
        self.anna = self.create_user('anna')

    def test_get_followings(self):
        user1 = self.create_user('user1')
        user2 = self.create_user('user2')
        for to_user in [user1, user2, self.anna]:
            Friendship.objects.create(from_user=self.lisa, to_user=to_user)
        # since we used signals, we don't need to manually invalidate cache

        user_id_set = FriendshipService.get_following_user_id_set(self.lisa.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id, self.anna.id})

        Friendship.objects.filter(from_user=self.lisa, to_user=self.anna).delete()
        user_id_set = FriendshipService.get_following_user_id_set(self.lisa.id)
        self.assertSetEqual(user_id_set, {user1.id, user2.id})
