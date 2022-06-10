"""
Code related to the product functionality
"""

import os, http, time, random, pathlib, flask, shutil
from flask import Flask, Blueprint, render_template, redirect, jsonify, request, session
from src.use_cases.products import get_product_params, publish_product, update_product, delete_product, list_products, get_reviews, list_reviews, edit_user_review, delete_user_review, delete_reviews, get_user_review, add_favorite, remove_favorite, delete_favorites, if_favorite
from src.use_cases.orders import new_order
from src.use_cases.carts import user_cart_info, new_cart, new_product, add_product, erase_cart_product, erase_cart, user_cart, user_cart_info_solo, update_cart_price, get_cart_price
from src.use_cases.register import get_user_info, get_user_id, update_credit
from src.use_cases.user import get_user_from_id
from src.web.auth import requires_access_level, log_vars
from datetime import date, datetime
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from src.config import *

product = Blueprint('product', __name__, template_folder='templates')

def show_cart(user_id):
    cart_products = []
    carts = user_cart_info(user_id, "ongoing")

    if len(carts) == 0:
        cart_id = None
        cart_price = "0.00"
        cart_products = None
    
    elif len(carts) != 0:
        for user_id, cart_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status in carts:
            cart_products.append((cart_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, status))

    return cart_products, cart_price, cart_id 

#Private API
@product.route("/<path:category>/<path:product_id>", methods=['POST', 'GET']) #Will show product info to everyone, will allow checking reviews and add to basket to session users
def product_path(product_id, category):
    product_id, image, description, title, category, price, discount, discounted_price, stock, vendor, active, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(int(product_id))
    image_group = []
    for file in os.listdir(image):
        image = file
        image_group.append((image))
    price = round(price)
    discounted_price = round(discounted_price)
    discount = round(discount)
    if "user" in session:
        logged_in = True
        myname, credit = get_user_info(session['user'])
        user_id = get_user_id(session['user'])[0]
        clearance = get_user_from_id(user_id)[1]
        favorited = if_favorite(user_id, product_id)

        if favorited is not None:
            fav_active = 1
        else:
            fav_active = 0

        if request.method == 'POST' and "favorite_btn" in request.form:
            return toggle_favorite(product_id)

        if request.method == 'POST' and "add_basket" in request.form:
            return add_basket(product_id)
        
        review_list = []
        reviews = get_reviews(product_id)
        for review_user_id, review_title, review_rating, review_content in reviews:
            review_list.append((myname, review_title, review_rating, review_content))

        cart_products, cart_price, cart_id = show_cart(user_id)

        return render_template("ProductTemplate.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, review_list=review_list, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id, image_group=image_group, description=description, title=title, category=category, price=price, discount=discount, discounted_price=discounted_price, stock=stock, vendor=vendor, meta_title=meta_title, meta_description=meta_description, meta_tags=meta_tags, slug=slug, fav_active=fav_active)
    else:
        myname = ''
        credit = 0
        logged_in = False
        clearance = 0

        if request.method == 'POST' and "add_basket" in request.form:
            return redirect('/Login')

        return render_template("ProductTemplate.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, image=image, description=description, title=title, category=category, price=price, discount=discount, discounted_price=discounted_price, meta_title=meta_title, meta_description=meta_description, meta_tags=meta_tags, slug=slug)

def toggle_favorite(product_id):
    product_id, image, description, product_title, category, product_price, product_discount, discounted_price, stock, vendor, active, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(int(product_id))
    user_id = get_user_id(session['user'])[0]
    favorited = if_favorite(user_id, product_id)

    if favorited is not None:
        remove_favorite(user_id, product_id)
    else:
        add_favorite(user_id, product_id)

    return redirect('/' + str(category) + '/' + str(product_id))

def add_basket(product_id):
    product_id, image, description, product_title, category, product_price, product_discount, discounted_price, stock, vendor, active, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(int(product_id))
    user_id = get_user_id(session['user'])[0]

    cart_exists = user_cart_info(int(user_id), "ongoing")
    same_product = user_cart_info_solo(int(user_id), product_id, "ongoing")
    added_qty = 1
 
    if added_qty == 0:
        return bad_request_response('Cant buy zero')

    if cart_exists == []:
        cart_price = (discounted_price * added_qty)
        new_cart(user_id, product_id, product_title, added_qty, product_price, product_discount, discounted_price, cart_price, "ongoing")

    elif same_product != None:
        user_id, cart_id, product_total = same_product[0], same_product[1], same_product[7]
        cart_price = (product_total * added_qty)
        add_product(added_qty, cart_price, user_id, cart_id, product_id)
        cart_products, cart_price, cart_id = show_cart(user_id)  #FIXME Maybe theres a easier way to update me
        update_cart_price(cart_price, cart_id)

    elif len(cart_exists) != 0 and same_product == None:
        cart_list = []
        cart_id = user_cart(user_id, "ongoing")
        for past_product_price, past_product_qty in get_cart_price(cart_id):
            past_cart_price = (past_product_price * past_product_qty)
            cart_list.append((past_cart_price))
        cart_price = (discounted_price * added_qty) + sum(cart_list)
        new_product(cart_id, user_id, product_id, product_title, added_qty, product_price, product_discount, discounted_price, cart_price, "ongoing")
        update_cart_price(cart_price, cart_id)

    else:
        bad_request_response('oopsie')

    return redirect('/' + str(category) + '/' + str(product_id))

@product.route('/del_cart_product/<int:cart_id>/<int:product_id>', methods=['POST', 'GET'])
def remove_product(cart_id, product_id):
    user_id = get_user_id(session['user'])[0]
    erase_cart_product(user_id, cart_id, product_id)

    cart_list = []
    for past_product_price, past_product_qty in get_cart_price(cart_id):
        past_cart_price = (past_product_price * past_product_qty)
        cart_list.append((past_cart_price))

    cart_price = sum(cart_list)
    update_cart_price(cart_price, cart_id)

    return redirect(request.referrer) #Use redirect(request.url) if you don't use an endpoint to perform a function (otherwise use the current, it will keep you on the same page)

@product.route('/del_cart/<int:cart_id>', methods=['POST', 'GET'])
def remove_cart(cart_id):
    user_id = get_user_id(session['user'])[0]
    cart_id = user_cart(user_id, "ongoing")

    erase_cart("dropped", user_id, cart_id)

    return redirect(request.referrer)

#AdminControlPanel
@product.route('/TheBrain/ManageProducts/Edit', methods=['POST', 'GET'])
@requires_access_level(2)
def choose_product():
    logged_in, myname, credit, user_id, clearance = log_vars(session)
    form = request.form

    if request.method == 'POST' and "product_id" in form:
        product_id = form['product_id']
        product_id, image, description, title, category, price, discount, discounted_price, stock, vendor, active, meta_title, meta_description, meta_tags, slug, created_at = get_product_params(int(product_id))
        if request.method == 'POST' and "title" in form:
            return edit_product(title)
        return render_template("Edit.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, product_id=product_id, image=image, description=description, title=title, category=category, price=price, discount=discount, discounted_price=discounted_price, stock=stock, vendor=vendor, meta_title=meta_title, meta_description=meta_description, meta_tags=meta_tags, slug=slug)

    return render_template("Edit.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

def edit_product(title):
    form = request.form

    def allowed_file(image):
        return '.' in image and \
                image.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    old_title = title
    product_id = form['product_id']
    title = form['title']
    if old_title != title:
        source = pathlib.Path(UPLOAD_FOLDER, old_title)
        destination = pathlib.Path(UPLOAD_FOLDER, title)
        os.rename(source, destination)
    images = flask.request.files.getlist('image')
    if not images or not any(f for f in images):
        images = None
    else:
        for image in images:
            image_test = secure_filename(image.filename)
            if allowed_file(image_test) == False:
                return bad_request_response(f'We offer a strict variety of png, jpg, jpeg and gif, they are very very good and very very cheap')
        for image in images:
            image.save(os.path.join(UPLOAD_FOLDER, title, secure_filename(image.filename)))

    description = form['description']
    category = form['category']
    price = form['price']
    discount = form['discount']
    stock = form['stock_qty']
    vendor = form['vendor']
    meta_title = form['meta_title']
    meta_description = form['meta_description']
    meta_tags = form['meta_tags']
    slug = form['slug']

    image_path = str(pathlib.Path(UPLOAD_FOLDER, title))

    update_product(image_path, description, title, category, price, discount, vendor, stock, meta_title, meta_description, meta_tags, slug, product_id)
    return redirect('/' + str(category) + '/' + str(product_id))

#AdminControlPanel
@product.route('/register_product', methods=['POST'])
@requires_access_level(2)
def register_product():
    files = request.files
    params = ('image',)

    form = request.form
    params = ('csrf_token', 'description', 'title', 'category', 'price', 'discount', 'vendor', 'stock_qty', 'meta_title', 'meta_description', 'meta_tags', 'slug')

    if form is None or len(form) != len(params):
        return bad_request_response('Invalid number of arguments')

    for param in params:
        if param not in form:
            return bad_request_response(f'I need a {param} parameter')

    def allowed_file(image):
        return '.' in image and \
                image.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    #TODO - Call validators
    title = form['title']
    images = flask.request.files.getlist('image')
    for image in images:
        image_test = secure_filename(image.filename)
        if allowed_file(image_test) == False:
            return bad_request_response(f'We offer a strict variety of png, jpg, jpeg and gif, they are very very good and very very cheap, or just upload a picture')
    
    pathlib.Path(UPLOAD_FOLDER, title).mkdir(exist_ok=True)

    for image in images:
        image.save(os.path.join(UPLOAD_FOLDER, title, secure_filename(image.filename)))

    category = form['category']
    description = form['description']
    price = form['price']
    discount = form['discount']
    discounted_price = int(price) - ((int(price) * int(discount)) / 100)
    stock = form['stock_qty']
    vendor = form['vendor']
    meta_title = form['meta_title']
    meta_description = form['meta_description']
    meta_tags = form['meta_tags']
    slug = form['slug']

    image_path = str(pathlib.Path(UPLOAD_FOLDER, title))

    try:
        product_id = publish_product(image_path, description, title, category, price, discount, discounted_price, stock, vendor, meta_title, meta_description, meta_tags, slug)
        return redirect('/' + str(category) + '/' + str(product_id))  #TODO - Pass product_id
    except EventAlreadyExistsException as e:
        return bad_request_response(f'An error occured when publishing the product {e}')

#AdminControlPanel
@product.route('/erase_product', methods=['POST'])
@requires_access_level(2)
def erase_product():
    product_id = request.form['product_id']
    title = get_product_params(int(product_id))[3]
    delete_reviews(product_id)
    delete_favorites(product_id)
    delete_product(product_id)
    shutil.rmtree(pathlib.Path(UPLOAD_FOLDER, title), ignore_errors=True)
    #FIXME - delete lootbox and lootboxinv with product_id
    return redirect('/TheBrain')

#AdminControlPanel
@product.route('/TheBrain/ManageProducts/List', methods=['GET'])
@requires_access_level(2)
def lists_products():
    logged_in, myname, credit, user_id, clearance = log_vars(session)

    result = []
    products = list_products()

    for product_id, title, category, price, active, created_at in products:
        result.append((product_id, title, category, price, active, created_at))

    return render_template("ProductList.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

#AdminControlPanel
@product.route('/TheBrain/ManageReviews/ListReviews', methods=['GET'])
@requires_access_level(2)
def lists_reviews():
    logged_in, myname, credit, user_id, clearance = log_vars(session)

    result = []
    reviews = list_reviews()

    for review_id, user_id, product_id, review_title, review_rating, review_content, active, created_at in reviews:
        result.append((review_id, user_id, product_id, review_title, review_rating, review_content, active, created_at))

    return render_template("ReviewList.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

#AdminControlPanel
@product.route('/TheBrain/ManageReviews/EditReview', methods=['POST', 'GET'])
@requires_access_level(2)
def edit_review():
    logged_in, myname, credit, user_id, clearance = log_vars(session)
    form = request.form

    if request.method == 'POST' and "review_id" in form:
        review_id = form['review_id']
        review_title, review_rating, review_content = get_user_review(review_id)
        return render_template("EditReview.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, review_id=review_id, review_title=review_title, review_rating=review_rating, review_content=review_content)

    return render_template("EditReview.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

#AdminControlPanel
@product.route('/Updating_UserReview', methods=['POST', 'GET'])
@requires_access_level(2)
def Updating_UserReview():
    form = request.form

    if request.method == 'POST' and "review_title" in form:
        review_title = form['review_title']
        review_rating = form['review_rating']
        review_content = form['review_content']
        info_list = [review_title, review_rating, review_content]
        conv = lambda i : i or None
        res = [conv(i) for i in info_list]
        review_title = res[0]
        review_rating = res[1]
        review_content = res[2]
        review_rating = (int(review_rating) / 20)
        review_id = form['review_id'] #FIXME Find out how to remove the extra review_id input
        edit_user_review(review_title, review_rating, review_content, review_id)
        return redirect('/TheBrain/ManageReviews/EditReview')

    return redirect('/TheBrain/ManageReviews/EditReview')

#AdminControlPanel
@product.route('/erase_review', methods=['POST'])
@requires_access_level(2)
def erase_review():
    review_id = request.form['review_id']
    delete_user_review(review_id)
    return redirect('/TheBrain')

def bad_request_response(reason):
    '''
        FIXME: Put this in a utils.py
    '''
    response = jsonify({'reason': reason})
    response.status_code = http.HTTPStatus.BAD_REQUEST
    return response
