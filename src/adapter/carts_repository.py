import psycopg2, os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class CartsRepository:

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
                print('[+] Carts database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS carts (
                                        cart_id SERIAL,
                                        user_id INT NOT NULL,
                                        product_id INT NOT NULL,
                                        product_title VARCHAR ( 100 ) NOT NULL,
                                        product_qty INT NOT NULL,
                                        product_subtotal numeric ( 8 , 2 ) NOT NULL,
                                        product_discount DECIMAL(5,2) CHECK (product_discount >= 0 AND product_discount <= 100.00) DEFAULT 0.00,
                                        product_total numeric ( 8 , 2 ) NOT NULL,
                                        cart_price numeric ( 8 , 2 ) NOT NULL,
                                        status VARCHAR (32) DEFAULT 'Ativo' NOT NULL,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                                );'''
            cursor.execute(sql_create_table)

    def user_cart(self, user_id, status):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT cart_id FROM carts WHERE user_id=%s AND status=%s;", (user_id, status))
            result = cursor.fetchone()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return []

    def user_cart_info(self, user_id, status):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT user_id, cart_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status FROM carts WHERE user_id=%s AND status=%s;", (user_id, status))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return []

    def user_cart_info_solo(self, user_id, product_id, status):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT user_id, cart_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status FROM carts WHERE user_id=%s AND product_id=%s AND status=%s;", (user_id, product_id, status))
            result = cursor.fetchone()
            return result

    def cart_product(self, user_id, cart_id, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT cart_id, product_id FROM carts WHERE user_id=%s AND cart_id=%s AND product_id=%s;", (user_id, cart_id, product_id))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return []

    def new_cart(self, user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status):
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO carts(user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING cart_id;",
                            (user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status))
            cart_id = cursor.fetchone()
        return cart_id[0]

    def new_product(self, cart_id, user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status):
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO carts(cart_id, user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                            (cart_id, user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status))

    def add_product(self, product_qty, cart_price, user_id, cart_id, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE carts SET product_qty=product_qty + %s, cart_price=cart_price + %s, last_updated = CLOCK_TIMESTAMP() WHERE user_id=%s AND cart_id=%s AND product_id=%s;", (product_qty, cart_price, user_id, cart_id, product_id))

    def erase_cart_product(self, user_id, cart_id, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM carts WHERE user_id=%s AND cart_id=%s AND product_id=%s;", (user_id, cart_id, product_id))

    def erase_cart(self, status, user_id, cart_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE carts SET status=%s WHERE user_id=%s AND cart_id=%s;", (status, user_id, cart_id))
    
    def get_cart_price(self, cart_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT product_total, product_qty FROM carts WHERE cart_id=%s;", (cart_id,))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return []

    def get_my_cart_price(self, user_id, status):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT product_qty, product_subtotal, product_discount, product_total, cart_price FROM carts WHERE user_id=%s AND status=%s;", (user_id, status))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return []

    def update_cart_price(self, cart_price, cart_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE carts SET cart_price=%s WHERE cart_id=%s;", (cart_price, cart_id))

database_carts = CartsRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=carts_db_name)