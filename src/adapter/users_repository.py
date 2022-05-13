"""
Functions that query the database
    emails are 320 chars
    Passwords are 64 chars because we use sha256 (hex digested)

    NOTE: If we change the table structure (number of columns, etc), we need to migrate/remove the current table
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *


class UsersRepository:

    def __init__(self, host, port, user, password, db_name):
        """ Create users and domain databases """
        self.con = psycopg2.connect(
            user=user, password=password, host=host, port=port)
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # Light-weight object. Fine to create one for each transaction
        with self.con.cursor() as cursor:
            # Create database if not exists
            sql_create_database = f"CREATE DATABASE {db_name};"
            try:
                cursor.execute(sql_create_database)
            except psycopg2.errors.DuplicateDatabase:
                print('[+] Users database already exists')  # Which is fine

            # Create table for users if it does not exist
            sql_create_table = f'''CREATE TABLE IF NOT EXISTS users (
                                        user_id SERIAL PRIMARY KEY,
                                        email VARCHAR ( 320 ) UNIQUE NOT NULL,
                                        password VARCHAR ( 64 ) NOT NULL,
                                        myname VARCHAR ( 64 ) NOT NULL,
                                        surname VARCHAR ( 64 ) NOT NULL,
                                        credit INT,
                                        birthday VARCHAR ( 64 ),
                                        clearance INT DEFAULT 1,
                                        salt VARCHAR ( 8 ) NOT NULL,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                );'''
            cursor.execute(sql_create_table)


    def valid_login(self, user, pwd):
        """
            Checks whether there is an entry in the DB that maps <user> to <pwd>
                This function is responsible for hashing the password before checking!

            user and pwd --> strings, not bytes!
        """

        # IMPORTANT - Use the with statement to close transactions, even for SELECT statements
        #               Also, keep transactions short
        with self.con.cursor() as cursor:
            # IMPORTANT - Use the %s syntax to avoid SQL injection vulnerabilities
            cursor.execute(
                "SELECT password, salt FROM users WHERE email=%s", (user,))
            result = cursor.fetchall()

        if len(result) != 1:  # User does not exist
            return None
        return result[0]

    def insert_user(self, email, hashed_password, myname, surname, salt):
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO users(email, password, myname, surname, salt) VALUES (%s, %s, %s, %s, %s);",
                           (email, hashed_password, myname, surname, salt))

    def update_credit(self, credit, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE users SET credit=%s WHERE user_id=%s;", (credit, user_id))

    def get_user(self, email):
        with self.con.cursor() as cursor:
            cursor.execute(
                "SELECT email, password, salt FROM users WHERE email=%s;", (email,))
            result = cursor.fetchall()
            if len(result) != 1:  # User does not exist
                return None
            return result[0]

    def get_user_info(self, email):
        with self.con.cursor() as cursor:
            cursor.execute(
                "SELECT myname, credit FROM users WHERE email=%s;", (email,))
            result = cursor.fetchone()
            result = list(result)
            if result[1] == None:
                result [1] = 0
                result = tuple(result)
                return result
            else:
                result = tuple(result)
                return result

    def clean_db_users(self):
        with self.con.cursor() as cursor:
            cursor.execute("TRUNCATE users, reviews, orders, payments, carts, lootboxinv")#FIXME alot of dependent tables, figure this out to a better solution
    
    def change_password(self, password, email):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE users SET password=%s WHERE email=%s;", (password, email))

    def delete_account(self, user_id, password):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id=%s AND password=%s;", (user_id, password))

    def get_user_id(self, email):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT user_id, credit FROM users WHERE email=%s;", (email,))
            result = cursor.fetchone()
            return result

    def update_info(self, myname, surname, email, birthday, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE users SET myname = COALESCE(%s, myname), surname = COALESCE(%s, surname), email = COALESCE(%s, email), birthday = COALESCE(%s, birthday) WHERE user_id=%s;", (myname, surname, email, birthday, user_id))

    def get_user_from_id(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute(
                "SELECT email, clearance FROM users WHERE user_id=%s;", (user_id,))
            result = cursor.fetchall()
            if len(result) != 1:  # User does not exist
                return None
            return result[0]

    def list_users(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT user_id, email, credit, myname, surname, birthday, created_at FROM users;")
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                return None

    def delete_user(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id=%s;", (user_id,))

    def list_user_info(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT myname, surname, email, birthday FROM users WHERE user_id=%s;", (user_id,))
            result = cursor.fetchone()
            return result

    def manage_clearance(self, clearance_number, chosen_user_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE users SET clearance = COALESCE(%s, clearance) WHERE user_id=%s;", (clearance_number, chosen_user_id))

database_users = UsersRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=users_db_name)


    #FUTURE - def confirm_email(self, confirmed, email):
        #with self.con.cursor() as cursor:
            #cursor.execute("UPDATE users SET confirmed = TRUE WHERE email=%s;", (confirmed, email))