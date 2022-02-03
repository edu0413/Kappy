import json
import unittest
from unittest.mock import create_autospec
from flask import Flask

from src.use_cases import register

register.register_login = create_autospec(register.register_login)
from src.web.auth import auth


class TestRegister(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(auth)
        self.app = self.app.test_client()
        self.valid_data = {'name': 'Valid Name',
                           'email': 'valid@email.com',
                           'username': 'username123_',
                           'password': 'some_password'}
        register.register_login.reset_mock()

    def test_invalid_number_arguments_in_body(self):
        test_cases = [
            None,
            {'name': ''},
            {'name': '', 'email': ''},
            {'name': '', 'email': '', 'address': ''}
        ]

        for tc in test_cases:
            response = self.app.post('/register', data=tc)
            self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['reason'], "Invalid number of arguments")
            register.register_login.assert_not_called()

    def test_missing_field_in_body(self):
        test_cases = [
            ({'not_name': 'asd', 'email': 'email@bla.pt', 'username': 'wer', 'password': 'wer'}, 'Missing name field'),
            ({'name': 'asd', 'not_email': 'email@bla.pt', 'username': 'wer', 'password': 'wer'}, 'Missing email field'),
            ({'name': 'asd', 'email': 'email@bla.pt', 'not_username': 'wer', 'password': 'wer'}, 'Missing username '
                                                                                                 'field'),
            ({'name': 'asd', 'email': 'email@bla.pt', 'username': 'wer', 'not_password': 'wer'}, 'Missing password '
                                                                                                 'field')
        ]

        for tc in test_cases:
            expected_reason = tc[1]
            response = self.app.post('/register', data=tc[0])

            self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['reason'], expected_reason)
            register.register_login.assert_not_called()

    def test_invalid_name(self):
        invalid_name_json = self.valid_data
        invalid_name_json['name'] = '!nvalid Name'
        response = self.app.post('/register', data=invalid_name_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid name")
        register.register_login.assert_not_called()

    def test_invalid_email(self):
        invalid_email_json = self.valid_data
        invalid_email_json['email'] = 'email'
        response = self.app.post('/register', data=invalid_email_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid email")
        register.register_login.assert_not_called()

    def test_invalid_username(self):
        invalid_username_json = self.valid_data
        invalid_username_json['username'] = 'username!!!'
        response = self.app.post('/register', data=invalid_username_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid username")
        register.register_login.assert_not_called()

    def test_invalid_password(self):
        invalid_password_json = self.valid_data
        invalid_password_json['password'] = '@something!#reallycrazy?'
        response = self.app.post('/register', data=invalid_password_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid password")
        register.register_login.assert_not_called()

    def test_happy_path(self):
        response = self.app.post('/register', data=self.valid_data)

        self.assertIs(response.status_code, 200, 'The status code should be 200 OK.')
        register.register_login.assert_called_with(self.valid_data['username'], self.valid_data['password'])


if __name__ == "__main__":
    unittest.main()
