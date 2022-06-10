import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class FavoritesRepository:

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
                print('[+] Favorites database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS favorites (
                                        user_id INT NOT NULL,
                                        product_id INT NOT NULL,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                                );'''
            cursor.execute(sql_create_table)

    def add_favorite(self, user_id, product_id): #Will insert a new row with user_id, product_id
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO favorites(user_id, product_id) VALUES (%s, %s);", (user_id, product_id))

    def remove_favorite(self, user_id, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM favorites WHERE user_id=%s AND product_id=%s;", (user_id, product_id))

    def delete_favorites(self, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM favorites WHERE product_id=%s;", (product_id,))

    def if_favorite(self, user_id, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM favorites WHERE user_id=%s and product_id=%s", (user_id, product_id))
            result = cursor.fetchone()
            if result is not None:
                return result
            else:
                return None

    def show_user_favorite(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT product_id FROM favorites WHERE user_id=%s", (user_id,))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                return []


database_favorites = FavoritesRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=favorites_db_name)