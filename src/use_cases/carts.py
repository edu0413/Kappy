from src.adapter.carts_repository import database_carts

def user_cart(user_id, status):
    return database_carts.user_cart(user_id, status)

def user_cart_info(user_id, status):
    return database_carts.user_cart_info(user_id, status)

def user_cart_info_solo(user_id, product_id, status):
    return database_carts.user_cart_info_solo(user_id, product_id, status)

def cart_product(user_id, cart_id, product_id):
    return database_carts.cart_product(user_id, cart_id, product_id)

def new_cart(user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status):
    return database_carts.new_cart(user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status)

def new_product(cart_id, user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status):
    return database_carts.new_product(cart_id, user_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status)

def add_product(product_qty, cart_price, user_id, cart_id, product_id):
    return database_carts.add_product(product_qty, cart_price, user_id, cart_id, product_id)

def erase_cart_product(user_id, cart_id, product_id):
    return database_carts.erase_cart_product(user_id, cart_id, product_id)

def erase_cart(status, user_id, cart_id):
    return database_carts.erase_cart(status, user_id, cart_id)

def get_cart_price(cart_id):
    return database_carts.get_cart_price(cart_id)

def get_my_cart_price(user_id, status):
    return database_carts.get_my_cart_price(user_id, status)

def update_cart_price(cart_price, cart_id):
    return database_carts.update_cart_price(cart_price, cart_id)