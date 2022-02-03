import unittest
from src.web.validator import myName_validator, Surname_validator, postal_code_validator, email_validator, password_validator


class TestNameValidator(unittest.TestCase):
    def test_valid_name(self):
        test_cases = ['Hey', 'My name']

        for tc in test_cases:
            valid = myName_validator(tc)
            self.assertTrue(valid, tc + " is a valid name")

    def test_invalid_name(self):
        test_cases = ['', 'asd321!@#$%&/!("9]=?»', 'ha ', 'a very interesting name and also very long']

        for tc in test_cases:
            not_valid = myName_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid name")


class TestEmailValidator(unittest.TestCase):
    def test_valid_email(self):
        test_cases = ['hellow@smt.com',
                      'he-llo_w@smt.another.com']

        for tc in test_cases:
            valid = email_validator(tc)
            self.assertTrue(valid, tc + " is a valid email")

    def test_invalid_email(self):
        test_cases = [
            "hellow",
            "nani@",
            "@ac.com"
            "almost!@valid.al.co"
        ]

        for tc in test_cases:
            not_valid = email_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid name")


class TestUsernameValidator(unittest.TestCase):
    def test_valid_username(self):
        test_cases = [
            'username',
            'username123',
            'username123_-'
        ]

        for tc in test_cases:
            valid = Surname_validator(tc)
            self.assertTrue(valid, tc + " is a valid username")

    def test_invalid_username(self):
        test_cases = [
            "user name",
            "!!!@344"
        ]

        for tc in test_cases:
            not_valid = Surname_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid username")


class TestPasswordValidator(unittest.TestCase):
    def test_valid_password(self):
        test_cases = [
            'username',
            'username123',
            'username123_-'
        ]

        for tc in test_cases:
            valid = password_validator(tc)
            self.assertTrue(valid, tc + " is a valid username")

    def test_invalid_password(self):
        test_cases = [
            "user name",
            "!!!@344"
        ]

        for tc in test_cases:
            not_valid = password_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid username")


if __name__ == "__main__":
    unittest.main()
