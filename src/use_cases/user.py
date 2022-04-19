from src.adapter.users_repository import database_users
from src.adapter.favorites_repository import database_favorites

def get_user(email):
    return database_users.get_user(email)

def get_user_from_id(user_id):
    return database_users.get_user_from_id(user_id)

def delete_account(user_id, password):
    return database_users.delete_account(user_id, password)

def update_info(myname, surname, email, birthday, address, postal_code, country, cellphone, user_id):
    return database_users.update_info(myname, surname, email, birthday, address, postal_code, country, cellphone, user_id)

def change_password(password, email):
    return database_users.change_password(password, email)

def confirm_email(confirmed, email):
    return database_users.change_password(confirmed, email)

def list_users():
    return database_users.list_users()

def delete_user(user_id):
    return database_users.delete_user(user_id)

def list_user_info(user_id):
    return database_users.list_user_info(user_id)

def manage_clearance(clearance_number, chosen_user_id):
    return database_users.manage_clearance(clearance_number, chosen_user_id)

def add_favorite(user_id, product_id):
    return database_favorites.add_favorite(user_id, product_id)

def remove_favorite(user_id, product_id):
    return database_favorites.remove_favorite(user_id, product_id)

def if_favorite(user_id, product_id):
    return database_favorites.if_favorite(user_id, product_id)

def show_user_favorite(user_id):
    return database_favorites.show_user_favorite(user_id)
