import json
import unittest
#import flask_testing
from unittest.mock import create_autospec
from flask import Flask, Blueprint
#from flask_testing import TestCase| Uninstall flask_testing if not needed (and remove from reqs)

from src.use_cases import register

register.register_login = create_autospec(register.register_login)
from src.web.auth import auth
from src.web.product import product
from src.web.user import user
from src.web.payment import payment
from src.web.products_list import products_list
from src import config

class TestRegister(unittest.TestCase):
    render_templates = False
    def setUp(self):
        app = Flask('Kappy')
        app.register_blueprint(auth) # Register authentication endpoints
        app.register_blueprint(product) # Register everything about the seller (sell/products)
        app.register_blueprint(user) # Register additional user details
        app.register_blueprint(payment) # Payment functionalities
        app.register_blueprint(products_list)
        app.secret_key = config.SECRET_KEY
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_PERMANENT'] = False
        app.config['ENV'] = 'development'
        app.config['DEBUG'] = True
        app.config['UPLOAD_FOLDER'] = 'templates/assets/img'
        app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        # Set secret key for authenticated cookies
        self.app = app
        self.app.register_blueprint(auth)
        self.app.config['TESTING'] = True
        self.app.secret_key = config.SECRET_KEY
        self.app.register_blueprint(auth)
        self.app = self.app.test_client()
        self.valid_data = {'myname': 'Eduardo',
                           'surname': 'Deus',
                           'email': 'valid@email.com',
                           'postal_code': '2040-327',
                           'password': 'Thousand1000!'}
                           
        register.register_login.reset_mock()

    def test_invalid_number_arguments_in_body(self):
        test_cases = [
            None,
            {'myname': ''},
            {'myname': '', 'surname': ''},
            {'myname': '', 'surname': '', 'email': ''},
            {'myname': '', 'surname': '', 'email': '', 'postal_code': ''},
            {'myname': '', 'surname': '', 'email': '', 'postal_code': '', 'password': ''}
        ]

        for tc in test_cases:
            response = self.app.post('/Login', data=tc)
            print(response.headers)
            print(dir(response))
            self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['reason'], "Invalid number of arguments")
            register.register_login.assert_not_called()

    def test_missing_field_in_body(self):
        test_cases = [
            ({'not_myname': 'asd', 'surname': 'asdef', 'email': 'email@bla.pt', 'postal_code': 'wer', 'password': 'wer'}, 'Missing myname field'),
            ({'myname': 'asd', 'not_surname': 'asdef', 'email': 'email@bla.pt', 'postal_code': 'wer', 'password': 'wer'}, 'Missing surname field'),
            ({'myname': 'asd', 'surname': 'asdef', 'not_email': 'email@bla.pt', 'postal_code': 'wer', 'password': 'wer'}, 'Missing email field'),
            ({'myname': 'asd', 'surname': 'asdef', 'email': 'email@bla.pt', 'not_postal_code': 'wer', 'password': 'wer'}, 'Missing postal code field'),
            ({'myname': 'asd', 'surname': 'asdef', 'email': 'email@bla.pt', 'postal_code': 'wer', 'not_password': 'wer'}, 'Missing password field')
        ]

        for tc in test_cases:
            expected_reason = tc[1]
            response = self.app.post('/Login', data=tc[0])

            self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
            data = json.loads(response.get_data(as_text=True))
            self.assertEqual(data['reason'], expected_reason)
            register.register_login.assert_not_called()

    def test_invalid_myname(self):
        invalid_name_json = self.valid_data
        invalid_name_json['myname'] = '!nvalid Name'
        response = self.app.post('/Login', data=invalid_name_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid first name")
        register.register_login.assert_not_called()

    def test_invalid_surname(self):
        invalid_name_json = self.valid_data
        invalid_name_json['surname'] = '!nvalid Name!!!'
        response = self.app.post('/Login', data=invalid_name_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid last name")
        register.register_login.assert_not_called()

    def test_invalid_email(self):
        invalid_email_json = self.valid_data
        invalid_email_json['email'] = 'email'
        response = self.app.post('/Login', data=invalid_email_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid email")
        register.register_login.assert_not_called()

    def test_invalid_post_code(self):
        invalid_username_json = self.valid_data
        invalid_username_json['postal_code'] = '200000030!!!'
        response = self.app.post('/Login', data=invalid_username_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid postal code")
        register.register_login.assert_not_called()

    def test_invalid_password(self):
        invalid_password_json = self.valid_data
        invalid_password_json['password'] = '@something!#reallycrazy?'
        response = self.app.post('/Login', data=invalid_password_json)

        self.assertEqual(response.status_code, 400, 'The status code should be 400 BAD REQUEST.')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['reason'], "Invalid password")
        register.register_login.assert_not_called()

    def test_happy_path(self):
        response = self.app.post('/Login', data=self.valid_data)

        self.assertIs(response.status_code, 200, 'The status code should be 200 OK.')
        register.register_login.assert_called_with(self.valid_data['email'], self.valid_data['password'])


if __name__ == "__main__":
    unittest.main()
