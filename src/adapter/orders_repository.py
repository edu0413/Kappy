import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class OrdersRepository:

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
                print('[+] Orders database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS orders (
                                        order_id INT NOT NULL,
                                        user_id INT NOT NULL,
                                        product_id INT NOT NULL,
                                        product_qty INT NOT NULL,
                                        sub_total numeric ( 8 , 2 ) NOT NULL,
                                        total_discount DECIMAL(5,2) CHECK (total_discount >= 0 AND total_discount <= 100.00) NOT NULL,
                                        taxes numeric ( 8 , 2 ),
                                        shipping numeric ( 8 , 2 ),
                                        total_price numeric ( 8 , 2 ) NOT NULL,
                                        status VARCHAR( 64 ) DEFAULT 'A Aguardar Envio' NOT NULL,
                                        tracking_id VARCHAR( 64 ),
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                                );'''
            cursor.execute(sql_create_table)

    def new_order(self, order_id, user_id, product_id, product_qty, sub_total, total_discount, total_price): #Will insert a new row with user_id, product_id and qty_bought and returning the row id, called order_id
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO orders(order_id, user_id, product_id, product_qty, sub_total, total_discount, total_price) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                            (order_id, user_id, product_id, product_qty, sub_total, total_discount, total_price))

    def user_orders(self, user_id): #Will select the required fields inside orders and products table in order, to let the users collect info regarding their orders
        with self.con.cursor() as cursor:
            cursor.execute("SELECT orders.order_id, orders.user_id, orders.product_id, orders.product_qty, orders.total_price, orders.status, products.image, products.title, products.category, products.vendor, orders.created_at FROM products INNER JOIN orders ON products.product_id=orders.product_id WHERE user_id=%s;", (user_id,))
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

    def orders_list(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT orders.order_id, orders.user_id, orders.product_id, products.title, products.vendor, orders.status, orders.created_at FROM products INNER JOIN orders ON products.product_id=orders.product_id;")
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

database_orders = OrdersRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=orders_db_name)