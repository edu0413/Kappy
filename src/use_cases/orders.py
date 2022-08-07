from src.adapter.orders_repository import database_orders
from src.adapter.payments_repository import database_payments

def new_order(order_id, user_id, address_id, product_id, product_qty, sub_total, total_discount, total_price):
    return database_orders.new_order(order_id, user_id, address_id, product_id, product_qty, sub_total, total_discount, total_price)

def user_orders(user_id):
    return database_orders.user_orders(user_id)

def orders_list():
    return database_orders.orders_list()

def new_payment(user_id, order_id, address_id, entidade_id, referencia_id, amount_paid, pay_type, mode, receipt):
    return database_payments.new_payment(user_id, order_id, address_id, entidade_id, referencia_id, amount_paid, pay_type, mode, receipt)

def total_spent(user_id):
    return database_payments.total_spent(user_id)

def pay_status(order_id):
    return database_payments.pay_status(order_id)

def update_pay_status(payment_id, status, order_id):
    return database_payments.update_pay_status(payment_id, status, order_id)