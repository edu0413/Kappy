import os

db_user = 'postgres'
db_password = 'postgres'
users_db_name = os.getenv('POSTGRES_USERS_DB_NAME')
events_db_name = os.getenv('POSTGRES_EVENTS_DB_NAME')
customers_db_name = os.getenv('POSTGRES_CUSTOMERS_DB_NAME')
orders_db_name = os.getenv('POSTGRES_ORDERS_DB_NAME')