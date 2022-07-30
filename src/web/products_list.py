"""
Code related to the product listing
"""

import os, http, time
from flask import Blueprint, render_template, redirect, jsonify, request, session
from src.use_cases.products import get_all_ids, get_category_ids, get_product_params, publish_review, add_favorite, remove_favorite, if_favorite, show_user_favorite
from src.use_cases.orders import user_orders, pay_status
from src.use_cases.user import user_profile
from src.web.auth import requires_access_level, log_vars
from src.web.product import show_cart

products_list = Blueprint('products_list', __name__, template_folder='templates')

@products_list.route('/', methods=['POST', 'GET'])
def index():
    logged_in, myname, credit, user_id, clearance = log_vars(session)

    product_ids = [x[0] for x in get_all_ids()][-6:]
    result = []

    for product_id in product_ids:
        product_id, image, description, title, category, price, discount, discounted_price, stock, vendor, on_request, vendor_email, vendor_phone, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(product_id)
        for file in os.listdir(image):
            image = file
        price = round(price)
        discounted_price = round(discounted_price)
        if user_id != None:
            user_class = user_profile(user_id)[1]

            if user_class == 1:
                discount = round(discount) + round(2)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
            elif user_class == 2:
                discount = round(discount) + round(4)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
            elif user_class == 3:
                discount = round(discount) + round(6)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
            elif user_class == 4:
                discount = round(discount) + round(9)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
        result.append((product_id, image, title, category, price, discounted_price, on_request))

    product_ids = get_all_ids()
    Allresult = []

    for product_id in product_ids:
        product_id, image, description, title, category, price, discount, discounted_price, stock, vendor, on_request, vendor_email, vendor_phone, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(product_id)
        for file in os.listdir(image):
            image = file        
        price = round(price)
        discounted_price = round(discounted_price)
        if user_id != None:
            user_class = user_profile(user_id)[1]

            if user_class == 1:
                discount = round(discount) + round(2)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
            elif user_class == 2:
                discount = round(discount) + round(4)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
            elif user_class == 3:
                discount = round(discount) + round(6)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
            elif user_class == 4:
                discount = round(discount) + round(9)
                discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
        Allresult.append((product_id, image, title, category, price, discounted_price, on_request))

    ACresult, BBresult, CAresult, COresult, PRresult, JOresult, MAresult, RLresult, TCresult, VGresult = [], [], [], [], [], [], [], [], [], []
    categories = ["Acessórios", "Bebidas", "Calçado", "Cosméticos", "Perfumes", "Joalheria", "Malas", "Relógios", "Tecnologias", "Viagens"]
    for category in categories:
        product_ids = get_category_ids(category)
        for product_id in product_ids:
            product_id, image, description, title, category, price, discount, discounted_price, stock, vendor, on_request, vendor_email, vendor_phone, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(product_id)
            for file in os.listdir(image):
                image = file            
            price = round(price)
            discounted_price = round(discounted_price)
            if user_id != None:
                user_class = user_profile(user_id)[1]
                
                if user_class == 1:
                    discount = round(discount) + round(2)
                    discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
                elif user_class == 2:
                    discount = round(discount) + round(4)
                    discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
                elif user_class == 3:
                    discount = round(discount) + round(6)
                    discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
                elif user_class == 4:
                    discount = round(discount) + round(9)
                    discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))

            if category == "Acessórios":
                ACresult.append((product_id, image, title, "Acessórios", price, discounted_price, on_request))
            elif category == "Bebidas":
                BBresult.append((product_id, image, title, "Bebidas", price, discounted_price, on_request))
            elif category == "Calçado":
                CAresult.append((product_id, image, title, "Calçado", price, discounted_price, on_request))
            elif category == "Cosméticos":
                COresult.append((product_id, image, title, "Cosméticos", price, discounted_price, on_request))
            elif category == "Perfumes":
                PRresult.append((product_id, image, title, "Perfumes", price, discounted_price, on_request))
            elif category == "Joalheria":
                JOresult.append((product_id, image, title, "Joalheria", price, discounted_price, on_request))
            elif category == "Malas":
                MAresult.append((product_id, image, title, "Malas", price, discounted_price, on_request))
            elif category == "Relógios":
                RLresult.append((product_id, image, title, "Relógios", price, discounted_price, on_request))
            elif category == "Tecnologias":
                TCresult.append((product_id, image, title, "Tecnologias", price, discounted_price, on_request))
            elif category == "Viagens":
                VGresult.append((product_id, image, title, "Viagens", price, discounted_price, on_request))

    cart_products, cart_price, cart_id = show_cart(user_id)
    
    return render_template('index.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id, result=result, Allresult=Allresult, ACresult=ACresult, BBresult=BBresult, CAresult=CAresult, COresult=COresult, PRresult=PRresult, JOresult=JOresult, MAresult=MAresult, RLresult=RLresult, TCresult=TCresult, VGresult=VGresult)

@products_list.route('/myFavorites', methods=['POST', 'GET'])
@requires_access_level(1)
def list_favorites():
    logged_in, myname, credit, user_id, clearance = log_vars(session)

    product_ids = show_user_favorite(user_id)
    result = []

    for product_id in product_ids:
        product_id, image, description, title, category, price, discount, discounted_price, stock, vendor, on_request, vendor_email, vendor_phone, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(product_id)
        for file in os.listdir(image):
            image = file        
        price = round(price)
        discounted_price = round(discounted_price)
        user_class = user_profile(user_id)[1]

        if user_class == 1:
            discount = round(discount) + round(2)
            discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
        elif user_class == 2:
            discount = round(discount) + round(4)
            discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
        elif user_class == 3:
            discount = round(discount) + round(6)
            discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
        elif user_class == 4:
            discount = round(discount) + round(9)
            discounted_price = round(int(price) - ((int(price) * int(discount)) / 100))
        result.append((product_id, image, title, category, price, discounted_price))

    cart_products, cart_price, cart_id = show_cart(user_id)

    return render_template('myFavorites.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id, result=result)

@products_list.route('/myOrders', methods=['POST', 'GET'])
@requires_access_level(1)
def list_orders():
    logged_in, myname, credit, user_id, clearance = log_vars(session)

    result, result2 = [], []
    products = user_orders(user_id)

    for order_id, user_id, product_id, product_qty, total_price, status, image, title, category, vendor, created_at in products:
        for file in os.listdir(image):
            image = file            
        created_at = created_at.strftime('%d %b de %Y, %H:%M')
        payment_status = pay_status(order_id)
        for paymentstatus in payment_status:
            paymentstatus = paymentstatus[0]
        result.append((order_id, user_id, product_id, product_qty, total_price, status, paymentstatus, image, title, category, vendor, created_at)) #FIXME: Raise an exception if customer is not participating in products
    cart_products, cart_price, cart_id = show_cart(user_id)

    return render_template('myOrders.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id, result=result)

@products_list.route('/myReview/<path:category>/<path:product_id>', methods=['POST', 'GET'])
@requires_access_level(1)
def review_page(product_id, category):
    logged_in, myname, credit, user_id, clearance = log_vars(session)
    
    if request.method == 'POST' and "review_title" in request.form:
        return register_review(user_id, category, product_id)

    return render_template('myReview.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

def register_review(user_id, category, product_id):
    form = request.form
    params = ('csrf_token', 'review_title', 'review_rating', 'review_content')

    if form is None or len(form) != len(params):
        return bad_request_response('Invalid number of arguments')

    for param in params:
        if param not in form:
            return bad_request_response(f'I need a {param} parameter')

    review_title = form['review_title']
    review_rating = form['review_rating']
    review_content = form['review_content']
    review_rating = (int(review_rating) / 20)

    try:
        review_id = publish_review(user_id, product_id, review_title, review_rating, review_content)
        return redirect('/' + str(category) + '/' + str(product_id))
    except:
        return bad_request_response('An error occured when publishing the review')

def bad_request_response(reason):
    response = jsonify({'reason': reason})
    response.status_code = http.HTTPStatus.BAD_REQUEST
    return response