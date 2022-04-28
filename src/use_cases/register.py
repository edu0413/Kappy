import bcrypt as bcrypt
import psycopg2

from src.adapter.users_repository import database_users
from src.use_cases.auth_util import hash_password

def register_login(email, password, myname, surname):
    salt = bcrypt.gensalt().decode('utf-8')[:8]
    hash_pw = hash_password(password, salt)
    try:
        database_users.insert_user(email, hash_pw, myname, surname, salt)    #ask about the return true, why did it change everything
        return True
    except psycopg2.errors.UniqueViolation:
        raise UserAlreadyExists(email)

def get_user_info(email):
    return database_users.get_user_info(email)

def get_user_id(email):
    return database_users.get_user_id(email)

def update_credit(credit, user_id):
    return database_users.update_credit(credit, user_id)

class UserAlreadyExists(Exception):
    def __init__(self, user_id):
        super(Exception, self).__init__(f"User [{user_id}] already exists")
