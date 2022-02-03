from src.adapter.orders_repository import database_orders

def new_order(user_id, event_id, qty_bought):
    return database_orders.new_order(user_id, event_id, qty_bought)

def user_orders(user_id):
    return database_orders.user_orders(user_id)

def orders_list():
    return database_orders.orders_list()