import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class PaymentsRepository:

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
                print('[+] Payments database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS payments (
                                        transaction_id serial PRIMARY KEY,
                                        user_id INT NOT NULL,
                                        order_id INT,
                                        address_id INT NOT NULL,
                                        payment_id INT NOT NULL,
                                        amount_paid numeric ( 8 , 2 ) NOT NULL,
                                        pay_type VARCHAR( 64 ) NOT NULL,
                                        mode VARCHAR( 64 ) NOT NULL,
                                        status VARCHAR( 64 ) DEFAULT 'Pendente' NOT NULL,
                                        receipt VARCHAR( 100 ) NOT NULL,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        refund INT,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                                );'''
            cursor.execute(sql_create_table)

    def new_payment(self, user_id, order_id, address_id, payment_id, amount_paid, pay_type, mode, receipt): #Will insert a new row with user_id, product_id and qty_bought and returning the row id, called order_id
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO payments(user_id, order_id, address_id, payment_id, amount_paid, pay_type, mode, receipt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING transaction_id;",
                            (user_id, order_id, address_id, payment_id, amount_paid, pay_type, mode, receipt))
            transaction_id = cursor.fetchone()
        return transaction_id[0]

    def total_spent(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT order_id, amount_paid FROM payments WHERE user_id=%s;", (user_id,))
            result = cursor.fetchall()
            return result

    def pay_status(self, order_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT status FROM payments WHERE order_id=%s;", (order_id,))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                return []

    def update_pay_status(self, status, order_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE payments SET status=%s WHERE order_id=%s;", (status, order_id))

database_payments = PaymentsRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=payments_db_name)