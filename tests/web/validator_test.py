import unittest
from src.web.validator import name_validator, postal_code_validator, email_validator, password_validator


class TestNameValidator(unittest.TestCase):
    def test_valid_name(self):
        test_cases = ['Hey', 'Myname']

        for tc in test_cases:
            valid = name_validator(tc)
            self.assertTrue(valid, tc + " is a valid name")

    def test_invalid_name(self):
        test_cases = ['', 'asd321!@#$%&/!("9]=?»', 'ha ', 'a very interesting name and also very long']

        for tc in test_cases:
            not_valid = name_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid name")

class TestSurnameValidator(unittest.TestCase):
    def test_valid_surname(self):
        test_cases = ['Hey', 'Myname']

        for tc in test_cases:
            valid = name_validator(tc)
            self.assertTrue(valid, tc + " is a valid surname")

    def test_invalid_name(self):
        test_cases = ['', 'asd321!@#$%&/!("9]=?»', 'ha ', 'a very interesting name and also very long']

        for tc in test_cases:
            not_valid = name_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid surname")


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


class TestZipCodeValidator(unittest.TestCase):
    def test_valid_zipcode(self):
        test_cases = [
            '2040-327',
            '2040-322',
            '3000-320'
        ]

        for tc in test_cases:
            valid = postal_code_validator(tc)
            self.assertTrue(valid, tc + " is a valid postal_code")

    def test_invalid_zipcode(self):
        test_cases = [
            "user name",
            "!!!@344"
        ]

        for tc in test_cases:
            not_valid = postal_code_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid postal_code")


class TestPasswordValidator(unittest.TestCase):
    def test_valid_password(self):
        test_cases = [
            'Thousand500',
            'Thousand5999!!'
        ]

        for tc in test_cases:
            valid = password_validator(tc)
            self.assertTrue(valid, tc + " is a valid password")

    def test_invalid_password(self):
        test_cases = [
            "username",
            "user name",
            "!!!@344"
        ]

        for tc in test_cases:
            not_valid = password_validator(tc)
            self.assertFalse(not_valid, tc + " is not a valid password")


if __name__ == "__main__":
    unittest.main()
