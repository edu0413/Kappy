import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class LootboxInvRepository:

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
                print('[+] LootboxInv database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS lootboxinv (
                                        inventory_id serial PRIMARY KEY,
                                        user_id INT NOT NULL,
                                        lootbox_id INT NOT NULL,
                                        product_id INT NOT NULL,
                                        active BOOLEAN NOT NULL DEFAULT TRUE,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                                );'''
            cursor.execute(sql_create_table)

    def get_lootbox(self, user_id, lootbox_id, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO lootboxinv(user_id, lootbox_id, product_id) VALUES (%s, %s, %s) RETURNING inventory_id;", 
            (user_id, lootbox_id, product_id))
            inventory_id = cursor.fetchone()
        return inventory_id[0]

    def get_inv_ids(self, user_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT inventory_id FROM lootboxinv WHERE user_id=%s;", (user_id,))
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result
            
    def inventory_items(self, inventory_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT lootboxinv.inventory_id, lootbox.lootbox_id, products.category, products.product_id, products.image, lootbox.chances, lootboxinv.active FROM lootboxinv INNER JOIN lootbox ON lootbox.product_id=lootboxinv.product_id INNER JOIN products ON products.product_id=lootboxinv.product_id WHERE inventory_id=%s;", (inventory_id,))
            result = cursor.fetchone()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

database_lootboxinv = LootboxInvRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=lootboxinv_db_name)