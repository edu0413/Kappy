import unittest

from src.adapter.users_repository import database_users
from src.use_cases.auth_util import hash_password
from src.use_cases.login import login, PasswordNotFoundException, UserNotFoundException

class TestLogin(unittest.TestCase):
    def setUp(self):
        try:
            database_users.insert_user("email@email.com", hash_password("pwd", "010203"), "Eduardo", "Deus", "2040-327", "010203")
        except:
            pass

    def tearDown(self):
        database_users.delete_user('12')

    def test_valid_login(self):
        self.assertTrue(login('email@email.com', 'pwd'), 'The credentials email@email.com:pwd should be a valid login')

    def test_invalid_login_wrong_password(self):
        self.assertRaises(PasswordNotFoundException, login, 'email@email.com', 'pwd1')

    def test_invalid_login_nonexistent_user(self):
        self.assertRaises(UserNotFoundException, login, 'email2@email.com', 'pwd')

if __name__ == "__main__":
    unittest.main()
