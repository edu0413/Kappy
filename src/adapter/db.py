import os

db_user = 'postgres'
db_password = 'postgres'
users_db_name = os.getenv('POSTGRES_USERS_DB_NAME')
products_db_name = os.getenv('POSTGRES_PRODUCTS_DB_NAME')
carts_db_name = os.getenv('POSTGRES_CARTS_DB_NAME')
orders_db_name = os.getenv('POSTGRES_ORDERS_DB_NAME')
reviews_db_name = os.getenv('POSTGRES_REVIEWS_DB_NAME')
lootbox_db_name = os.getenv('POSTGRES_LOOTBOX_DB_NAME')
lootboxinv_db_name = os.getenv('POSTGRES_LOOTBOXINV_DB_NAME')
payments_db_name = os.getenv('POSTGRES_PAYMENTS_DB_NAME')
favorites_db_name = os.getenv('POSTGRES_FAVORITES_DB_NAME')