import unittest

from src.adapter.users_repository import database_users
from src.use_cases.register import register_login, UserAlreadyExists


class TestRegisterUseCase(unittest.TestCase):
    def tearDown(self):
        database_users.clean_db_users()

    def test_hash_password_then_insert(self):
        email = 'user'
        password = 'super_secret'
        myname = 'John'
        surname = 'Doe'
        postal_code = '2040-327'

        register_login(email, password, myname, surname, postal_code)

        actual_user = database_users.get_user(email)[0]
        self.assertEqual(email, actual_user, f"Expected {email} but got {actual_user}")

    def test_not_add_already_existing_user(self):
        email = 'user'
        password = 'super_secret'
        myname = 'John'
        surname = 'Doe'
        postal_code = '2040-327'

        register_login(email, password, myname, surname, postal_code)

        self.assertRaises(UserAlreadyExists, register_login, email, password, myname, surname, postal_code)
