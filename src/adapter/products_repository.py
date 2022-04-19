import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class ProductsRepository:

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
                print('[+] Products database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS products (
                                        product_id serial PRIMARY KEY,
                                        image VARCHAR (64) NOT NULL,
                                        description VARCHAR (1000) NOT NULL,
                                        title VARCHAR (100) NOT NULL,
                                        category VARCHAR (64) NOT NULL,
                                        price numeric (8, 2),
                                        discount DECIMAL(5, 2) CHECK (discount >= 0 AND discount <= 100.00) DEFAULT 0.00,
                                        discounted_price numeric (8, 2),
                                        stock INT NOT NULL,
                                        vendor VARCHAR (64) NOT NULL,
                                        active BOOLEAN NOT NULL DEFAULT TRUE,
                                        meta_title VARCHAR (100) NOT NULL,
                                        meta_description VARCHAR (160) NOT NULL,
                                        meta_tags VARCHAR (160) NOT NULL,
                                        slug VARCHAR (100) NOT NULL,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                );'''
            cursor.execute(sql_create_table)

#GENERATED BY DEFAULT AS IDENTITY

    def get_all_ids(self, active): #Will get all Event ID's, all you have to choose is if active is True or False
        with self.con.cursor() as cursor:
            cursor.execute("SELECT product_id FROM products WHERE active=bool(%s)", (active,))
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return []

    def get_category_ids(self, category, active): #Will get all Event ID's by categories, all you have to choose is the category and if active is True or False
        with self.con.cursor() as cursor:
            cursor.execute("SELECT product_id FROM products WHERE category=%s AND active=bool(%s);", (category, active)) 
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return []

    def get_product_params(self, product_id): #Will get all column data of a row based on the chosen product_id
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM products WHERE product_id=%s;", (product_id,))
            result = cursor.fetchone()
            if len(result) != 0:
                return result
            else:
                #FIXME - What happens when there is no product
                return None

    def publish_product(self, image, description, title, category, price, discount, discounted_price, stock, vendor, meta_title, meta_description, meta_tags, slug): #Will insert the requested Event data into the Products Table, and will return the product_id
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO products(image, description, title, category, price, discount, discounted_price, stock, vendor, meta_title, meta_description, meta_tags, slug) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING product_id;",
                           (image, description, title, category, price, discount, discounted_price, stock, vendor, meta_title, meta_description, meta_tags, slug))
            product_id = cursor.fetchone()
        return product_id[0]

    def update_product(self, image, description, title, category, price, discount, stock, vendor, meta_title, meta_description, meta_tags, slug, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE products SET image = COALESCE(%s, image), description = COALESCE(%s, description), title = COALESCE(%s, title), category = COALESCE(%s, category), price = COALESCE(%s, price), discount = COALESCE(%s, discount), vendor = COALESCE(%s, vendor), stock = COALESCE(%s, stock), meta_title = COALESCE(%s, meta_title), meta_description = COALESCE(%s, meta_description), meta_tags = COALESCE(%s, meta_tags), slug = COALESCE(%s, slug) WHERE product_id=%s;",
                           (image, description, title, category, price, discount, stock, vendor, meta_title, meta_description, meta_tags, slug, product_id))

    def delete_product(self, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM products WHERE product_id=%s;", (product_id,))

    def list_products(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT product_id, title, category, price, active, created_at FROM products;")
            result = cursor.fetchall()
            if len(result) != 0:
                return result
            else:
                return None

database_products = ProductsRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="5432", user=db_user, password=db_password, db_name=products_db_name)
