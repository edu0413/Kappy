from src.adapter.users_repository import database_users
from src.adapter.addresses_repository import database_addresses
from src.adapter.usersprofile_repository import database_usersprofile

def get_user(email):
    return database_users.get_user(email)

def get_user_from_id(user_id):
    return database_users.get_user_from_id(user_id)

def delete_account(user_id, password):
    return database_users.delete_account(user_id, password)

def update_info(myname, surname, email, birthday, user_id):
    return database_users.update_info(myname, surname, email, birthday, user_id)

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

def insert_profile(user_id):
    return database_usersprofile.insert_profile(user_id)

def update_outlay(user_class, class_milestone, class_expiration, class_days, total_spent, credits_bought, credits_spent, user_id):
    return database_usersprofile.update_outlay(user_class, class_milestone, class_expiration, class_days, total_spent, credits_bought, credits_spent, user_id)

def user_profile(user_id):
    return database_usersprofile.user_profile(user_id)

def new_address(user_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing):
    return database_addresses.new_address(user_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing)

def get_user_addresses(user_id):
    return database_addresses.get_user_addresses(user_id)

def get_user_address(user_id, address_id):
    return database_addresses.get_user_address(user_id, address_id)

def update_address(address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing, user_id, address_id):
    return database_addresses.update_address(address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing, user_id, address_id)

def update_shipping(main_shipping, user_id):
    return database_addresses.update_shipping(main_shipping, user_id)

def update_billing(main_billing, user_id):
    return database_addresses.update_billing(main_billing, user_id)

def delete_address(user_id, address_id):
    return database_addresses.delete_address(user_id, address_id)
