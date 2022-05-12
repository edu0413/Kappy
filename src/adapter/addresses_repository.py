import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class AddressesRepository:

    def __init__(self, host, port, user, password, db_name):
        """ Create users and domain databases """
        self.con = psycopg2.connect(
            user=user, password=password, host=host, port=port)
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        with self.con.cursor() as cursor:
            sql_create_database = f"CREATE DATABASE {db_name};"
            try:
                cursor.execute(sql_create_database)
            except psycopg2.errors.DuplicateDatabase:
                print('[+] Addresses database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS addresses (
                                        user_id INT NOT NULL,
                                        address_id SERIAL PRIMARY KEY,
                                        address_name VARCHAR( 64 ),
                                        full_name VARCHAR( 128 ),
                                        address VARCHAR ( 512 ),
                                        postal_code VARCHAR ( 8 ),
                                        city VARCHAR ( 64 ),
                                        country VARCHAR ( 64 ),
                                        phone_number VARCHAR ( 64 ),
                                        fiscal_number VARCHAR ( 64 ),
                                        main_shipping BOOLEAN,
                                        main_billing BOOLEAN,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                                );'''
            cursor.execute(sql_create_table)

    def new_address(self, user_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing):
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO addresses(user_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (user_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing))

    def get_user_addresses(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM addresses WHERE user_id=%s;", (user_id,))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                return []

    def get_user_address(self, user_id, address_id):
        with self.con.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM addresses WHERE user_id=%s AND address_id=%s;", (user_id, address_id))
            result = cursor.fetchone()
            return result

    def update_address(self, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing, user_id, address_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE addresses SET address_name = COALESCE(%s, address_name), full_name = COALESCE(%s, full_name), address = COALESCE(%s, address), postal_code = COALESCE(%s, postal_code), city = COALESCE(%s, city), country = COALESCE(%s, country), phone_number = COALESCE(%s, phone_number), fiscal_number = COALESCE(%s, fiscal_number), main_shipping = COALESCE(%s, main_shipping), main_billing = COALESCE(%s, main_billing) WHERE user_id=%s AND address_id=%s;", 
                            (address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing, user_id, address_id))

    def update_shipping(self, main_shipping, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE addresses SET main_shipping=bool(%s) WHERE user_id=%s;", (main_shipping, user_id))

    def update_billing(self, main_billing, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE addresses SET main_billing=bool(%s) WHERE user_id=%s;", (main_billing, user_id))

    def delete_address(self, user_id, address_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM addresses WHERE user_id=%s AND address_id=%s;", (user_id, address_id))

    def list_addresses(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM addresses;")
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                return None

database_addresses = AddressesRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=addresses_db_name)