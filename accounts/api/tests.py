from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from accounts.models import UserProfile
from testing.testcases import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'
USER_PROFILE_DETAIL_URL = '/api/profiles/{}/'

class AccountApiTests(TestCase):
    def setUp(self):
        self.clear_cache()
        # This function will be executed per test function is executed.
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@example.com',
            password='correct password',
        )

    def test_login(self):
        # 每个测试函数必须以 test_ 开头，才会被⾃动调⽤进⾏测试
        # Test function must start with test_, otherwise it won't be called automatically.
        # 测试必须⽤ post ⽽不是 get
        # Test should use post instead of get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 登录失败，http status code 返回 405 = METHOD_NOT_ALLOWED
        # log in fails, http status code returns 405
        self.assertEqual(response.status_code, 405)

        # ⽤了 post 但是密码错了
        # Test the situation that use post with wrong password.
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # 验证还没有登录
        # hasn't logged in yet
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # ⽤正确的密码
        # Use correct password.
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['id'], self.user.id)

        # 验证已经登录了
        # has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):

        # 先登录
        # Should log in first
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # 验证⽤户已经登录
        # User has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # 测试必须⽤ post
        # Testing requires post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # 改⽤ post 成功 logout
        # Success with post instead of get
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # 验证⽤户已经登出
        # Validate that user has logged out.
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # 测试 get 请求失败
        # use get
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # 测试错误的邮箱
        # Use email with bad format
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 测试密码太短
        # Use too short password
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 测试⽤户名太长
        # Use too long username
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 成功注册
        # sign up successfully
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        # Check if user profile has been created
        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)

        # 验证⽤户已经登⼊
        # Validate user has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)


class UserProfileAPITests(TestCase):
    def test_update(self):
        user1, user1_client = self.create_user_and_client('user1')
        profile = user1.profile
        profile.nickname = 'previous nickname'
        profile.save()
        url = USER_PROFILE_DETAIL_URL.format(profile.id)

        # profile should only be updated by its user
        _, user2_client = self.create_user_and_client('user2')
        response = user2_client.put(url, {
            'nickname': 'new nickname',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, 'previous nickname')

        # update nickname
        response = user1_client.put(url, {
            'nickname': 'new nickname',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertEqual(profile.nickname, 'new nickname')

        # update avatar
        response = user1_client.put(url, {
            'avatar': SimpleUploadedFile(
                name='my-avatar.jpg',
                content=str.encode('a fake image'),
                content_type='image/jpeg',
            ),
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('my-avatar' in response.data['avatar'], True)
        profile.refresh_from_db()
        self.assertIsNotNone(profile.avatar)
