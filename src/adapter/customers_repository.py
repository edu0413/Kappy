import psycopg2, os
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class CustomersRepository:

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
                print('[+] Customers database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS customers (
                                        user_id INT NOT NULL,
                                        event_id INT NOT NULL,
                                        tickets_bought INT NOT NULL,
                                        last_bought TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        first_bought TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                                        FOREIGN KEY (event_id) REFERENCES events(event_id),
                                        UNIQUE (user_id, event_id)
                                );'''
            cursor.execute(sql_create_table)

    def if_engaged(self, user_id, event_id): #Will select a row based on user_id and event_id and return false if no row is found, true if it is found
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM customers WHERE user_id=%s AND event_id=%s;", (user_id, event_id))
            result = cursor.fetchone()
            if result is None or len(result) == 0:  # Event Row does not exist
                return False
            else:
                return True

    def buy_ticket(self, user_id, event_id, tickets_bought, tickets_remaining): #Will insert respective id's for the tickets_bought and will update event_tickets on events table
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO customers(user_id, event_id, tickets_bought) VALUES (%s, %s, %s);", (user_id, event_id, tickets_bought))
            cursor.execute("UPDATE events SET event_tickets=%s WHERE event_id=%s", (tickets_remaining, event_id))

    def subscribe_again(self, tickets_bought, user_id, event_id, tickets_remaining): #Will update tickets_bought from the respective id's, let us know the timestamp of the update, will update event_tickets on events
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE customers SET tickets_bought=tickets_bought + %s, last_bought = CLOCK_TIMESTAMP() WHERE user_id=%s AND event_id=%s;", (tickets_bought, user_id, event_id))
            cursor.execute("UPDATE events SET event_tickets=%s WHERE event_id=%s", (tickets_remaining, event_id))

    def tickets_amount(self, event_id): #Will tell us the remaining tickets and the starting value of tickets based on the event_id
        with self.con.cursor() as cursor:
            cursor.execute("SELECT event_tickets, total_tickets FROM events WHERE event_id=%s;", (event_id,))
            result = cursor.fetchone()
            return result[0], result[1] #Because it is a tuple, result=[('number',)] result[0]='number' -- I still dont understand this, theres other queries that dont need it

    def get_participants(self, event_id): #Will showcase all participants and how many tickets they bought based on the event_id
        with self.con.cursor() as cursor:
            cursor.execute("SELECT user_id, tickets_bought FROM customers WHERE event_id=%s;", (event_id,))
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

    def user_events(self, user_id): #Will give a list of events where the user has purchased tickets
        with self.con.cursor() as cursor:
            cursor.execute("SELECT customers.user_id, customers.event_id, events.image, customers.tickets_bought, events.product_heading, events.category, events.event_tickets, events.sell_product_price, events.event_prompt, events.progress_perc, events.active FROM events INNER JOIN customers ON events.event_id=customers.event_id WHERE user_id=%s;", (user_id,))
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

    def subs_list(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT user_id, event_id, tickets_bought, last_bought, first_bought FROM customers;")
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

database_customers = CustomersRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=customers_db_name)