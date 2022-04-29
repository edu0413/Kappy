import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.adapter.db import *

class ReviewsRepository:

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
                print('[+] Reviews database already exists')

            sql_create_table = f'''CREATE TABLE IF NOT EXISTS reviews (
                                        review_id serial PRIMARY KEY,
                                        user_id INT NOT NULL,
                                        product_id INT NOT NULL,
                                        review_title VARCHAR( 64 ),
                                        review_rating INT CHECK (review_rating >= 0 AND review_rating <= 5) NOT NULL,
                                        review_content VARCHAR( 1000 ),
                                        active BOOLEAN NOT NULL DEFAULT TRUE,
                                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                        FOREIGN KEY (user_id) REFERENCES users(user_id),
                                        FOREIGN KEY (product_id) REFERENCES products(product_id)
                                );'''
            cursor.execute(sql_create_table)

    def publish_review(self, user_id, product_id, review_title, review_rating, review_content):
        with self.con.cursor() as cursor:
            cursor.execute("INSERT INTO reviews(user_id, product_id, review_title, review_rating, review_content) VALUES (%s, %s, %s, %s, %s) RETURNING review_id;",
            (user_id, product_id, review_title, review_rating, review_content))
            review_id = cursor.fetchone()
        return review_id[0]

    def get_reviews(self, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT user_id, review_title, review_rating, review_content FROM reviews WHERE product_id=%s;", (product_id,))
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

    def delete_reviews(self, product_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM reviews WHERE product_id=%s;", (product_id,))

    def list_reviews(self):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT * FROM reviews;")
            result = cursor.fetchall()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

    def get_user_review(self, review_id):
        with self.con.cursor() as cursor:
            cursor.execute("SELECT review_title, review_rating, review_content FROM reviews WHERE review_id=%s;", (review_id,))
            result = cursor.fetchone()
            if result is None or len(result) == 0:  # Event Row does not exist
                return []
            else:
                return result

    def edit_user_review(self, review_title, review_rating, review_content, review_id):
        with self.con.cursor() as cursor:
            cursor.execute("UPDATE reviews SET review_title = COALESCE(%s, review_title), review_rating = COALESCE(%s, review_rating), review_content = COALESCE(%s, review_content) WHERE review_id=%s;", (review_title, review_rating, review_content, review_id))

    def delete_user_review(self, review_id):
        with self.con.cursor() as cursor:
            cursor.execute("DELETE FROM reviews WHERE review_id=%s;", (review_id,))

database_reviews = ReviewsRepository(host=os.getenv("POSTGRES_HOSTNAME", "localhost"), port="80", user=db_user, password=db_password, db_name=reviews_db_name)