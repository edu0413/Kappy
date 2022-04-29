import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class LootboxRepository:

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
                print('[+] Lootbox database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS lootbox (
                                        lootbox_id INT NOT NULL,
                                        product_id INT NOT NULL,
                                        chances INT CHECK (chances >= 0 AND chances <= 100) NOT NULL,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                                );'''
            cursor.execute(sql_create_table)

    def publish_lootbox(self, lootbox_list):
        with self.con.cursor() as cursor:
            box_list = lootbox_list
            for l in box_list:
                cursor.execute("INSERT INTO lootbox(lootbox_id, product_id, chances) VALUES (%s, %s, %s) ;", l)

    def get_loot_ids(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT lootbox_id, product_id FROM lootbox;")
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result
            
    def lootbox_items(self, lootbox_id, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT lootbox.lootbox_id, products.category, products.product_id, products.image, products.title, lootbox.chances FROM products INNER JOIN lootbox ON products.product_id=lootbox.product_id WHERE lootbox.lootbox_id=%s AND products.product_id=%s;", (lootbox_id, product_id))
            result = cursor.fetchone()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

database_lootbox = LootboxRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=lootbox_db_name)