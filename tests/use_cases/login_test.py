import unittest

from src.adapter.users_repository import database_users
from src.use_cases.auth_util import hash_password
from src.use_cases.login import login, UserNotFoundException


class TestLogin(unittest.TestCase):
    def setUp(self):
        try:
            database_users.insert_user("user", hash_password("pwd", "010203"), "010203")
        except:
            pass

    def tearDown(self):
        database_users.delete_user('user')

    def test_valid_login(self):
        self.assertTrue(login('user', 'pwd'), 'The credentials user:pwd should be a valid login')

    def test_invalid_login_wrong_password(self):
        self.assertFalse(login('user', 'pwd1'), 'The credentials user:pwd1 should not be a valid login')

    def test_invalid_login_nonexistent_user(self):
        self.assertRaises(UserNotFoundException, login, 'user1', 'pwd')


if __name__ == "__main__":
    unittest.main()
