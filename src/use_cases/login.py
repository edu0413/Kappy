from src.adapter.users_repository import database_users
from src.use_cases.auth_util import hash_password

def login(email, pwd):
    row = database_users.get_user(email)

    if row is None:
        raise UserNotFoundException(email)

    _, hashed_pwd, salt = row
    hashed_pwd_provided = hash_password(pwd, salt)

    if hashed_pwd_provided != hashed_pwd:
        raise PasswordNotFoundException(pwd)
        
    return hashed_pwd_provided == hashed_pwd

class UserNotFoundException(Exception):
    def __init__(self, email):
        super(Exception, self).__init__(f"Could not find user [{email}]")

class PasswordNotFoundException(Exception):
    def __init__(self, pwd):
        super(Exception, self).__init__(f"Wrong password, try again")

class PasswordAlreadyExistsException(Exception):
    def __init__(self, pwd):
        super(Exception, self).__init__(f"This password is too similar to your last")