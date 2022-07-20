from src.adapter.products_repository import database_products
from src.adapter.reviews_repository import database_reviews
from src.adapter.favorites_repository import database_favorites

def get_all_ids():
    return database_products.get_all_ids()

def get_category_ids(category):
    return database_products.get_category_ids(category)

def get_product_params(product_id):
    return database_products.get_product_params(product_id)

def publish_product(image, description, title, category, price, discount, discounted_price, stock, vendor, on_request, vendor_email, vendor_phone, meta_title, meta_description, meta_tags, slug):
    try:
        return database_products.publish_product(image, description, title, category, price, discount, discounted_price, stock, vendor, on_request, vendor_email, vendor_phone, meta_title, meta_description, meta_tags, slug)
    except Exception as e:
        print(e)
        raise CouldntPublishEvent(e)

def update_product(image, description, title, category, price, discount, stock, vendor, meta_title, meta_description, meta_tags, slug, product_id):
    return database_products.update_product(image, description, title, category, price, discount, stock, vendor, meta_title, meta_description, meta_tags, slug, product_id)

def delete_product(product_id):
    return database_products.delete_product(product_id)

def list_products():
    return database_products.list_products()

def publish_review(user_id, product_id, review_title, review_rating, review_content):
    return database_reviews.publish_review(user_id, product_id, review_title, review_rating, review_content)

def get_reviews(product_id):
    return database_reviews.get_reviews(product_id)

def list_reviews():
    return database_reviews.list_reviews()

def get_user_review(review_id):
    return database_reviews.get_user_review(review_id)

def edit_user_review(review_title, review_rating, review_content, review_id):
    return database_reviews.edit_user_review(review_title, review_rating, review_content, review_id)

def delete_user_review(review_id):
    return database_reviews.delete_user_review(review_id)

def delete_reviews(product_id):
    return database_reviews.delete_reviews(product_id)

def add_favorite(user_id, product_id):
    return database_favorites.add_favorite(user_id, product_id)

def remove_favorite(user_id, product_id):
    return database_favorites.remove_favorite(user_id, product_id)

def delete_favorites(product_id):
    return database_favorites.delete_favorites(product_id)

def if_favorite(user_id, product_id):
    return database_favorites.if_favorite(user_id, product_id)

def show_user_favorite(user_id):
    return database_favorites.show_user_favorite(user_id)

class CouldntPublishEvent(Exception):
    def __init__(self, e):
        super(Exception, self).__init__(f"Could not publish product [{e}]")