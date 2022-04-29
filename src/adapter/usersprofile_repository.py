import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class UsersProfileRepository:

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
                print('[+] Usersprofile database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS usersprofile (
                                        user_id INT NOT NULL,
                                        user_class INT DEFAULT 0,
                                        class_expiration TIMESTAMP,
                                        class_days INT DEFAULT 0,
                                        money_spent INT DEFAULT 0,
                                        credits_bought INT DEFAULT 0,
                                        credits_spent INT DEFAULT 0,
                                        bought_prod_qty INT DEFAULT 0,
                                        bought_sil_box INT DEFAULT 0,
                                        bought_gol_box INT DEFAULT 0,
                                        bought_dia_box INT DEFAULT 0,
                                        reviews_made INT DEFAULT 0,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id)
                                );'''
            cursor.execute(sql_create_table)

    def insert_profile(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO usersprofile(user_id) VALUES (%s);", (user_id,))

    def user_profile(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM usersprofile WHERE user_id=%s;", (user_id,))
            result = cursor.fetchone()
            return result
    

database_usersprofile = UsersProfileRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="80", user=db_user, password=db_password, db_name=usersprofile_db_name)