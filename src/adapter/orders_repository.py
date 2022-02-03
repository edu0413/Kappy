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
                                        order_id serial PRIMARY KEY,
                                        user_id INT NOT NULL,
                                        event_id INT NOT NULL,
                                        tracking_id VARCHAR( 64 ),
                                        qty_bought INT NOT NULL,
                                        destination VARCHAR( 64 ),
                                        status VARCHAR( 64 ) DEFAULT 'Aguardando Envio' NOT NULL,
                                        review INT CHECK (review >= 0 AND review <= 5),
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        arrived_at VARCHAR( 64 ),
                                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                                        FOREIGN KEY (event_id) REFERENCES events(event_id)
                                );'''
            cursor.execute(sql_create_table)

    def new_order(self, user_id, event_id, qty_bought): #Will insert a new row with user_id, event_id and qty_bought and returning the row id, called order_id
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO orders(user_id, event_id, qty_bought) VALUES (%s, %s, %s) RETURNING order_id;",
                            (user_id, event_id, qty_bought))
            order_id = cursor.fetchone()
        return order_id[0]

    def user_orders(self, user_id): #Will select the required fields inside orders and events table in order, to let the users collect info regarding their orders
        with self.con.cursor() as cursor:
            cursor.execute("SELECT orders.order_id, orders.user_id, orders.event_id, orders.qty_bought, orders.status, events.image, events.product_heading, events.category, orders.created_at FROM events INNER JOIN orders ON events.event_id=orders.event_id WHERE user_id=%s;", (user_id,))
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

    def orders_list(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT orders.order_id, orders.user_id, orders.event_id, events.product_heading, orders.qty_bought, orders.status, orders.created_at FROM events INNER JOIN orders ON events.event_id=orders.event_id;")
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

database_orders = OrdersRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=orders_db_name)