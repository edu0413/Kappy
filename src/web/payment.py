"""
Code related to the payment
"""
import http
from flask import Blueprint, render_template, redirect, jsonify, request, session, url_for
from src.use_cases.orders import new_order, orders_list, new_payment
from src.use_cases.carts import user_cart, get_my_cart_price, erase_cart, user_cart_info
from src.use_cases.register import update_credit
from src.use_cases.user import list_user_info
from src.web.auth import requires_access_level, log_vars
from src.web.product import show_cart

payment = Blueprint('payment', __name__, template_folder='templates')

@payment.route('/myWallet', methods=['POST', 'GET'])
@requires_access_level(1)
def carteira():
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     if request.method == 'POST' and "buy_pack" in request.form:
          pack_price = request.form['buy_pack']
          return redirect(url_for('payment.confirm_pack_payment', pack_price=pack_price, **request.args))

     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template('myWallet.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

@payment.route('/PackCheckout', methods=['POST', 'GET'])
@requires_access_level(1)
def confirm_pack_payment():
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     pack_price = int(request.args['pack_price'])

     if request.method == 'POST' and "confirm_payment" in request.form:
          return finish_payment(pack_price)

     user_info = []
     myname, surname, email, birthday, address, postal_code, country, cellphone = list_user_info(user_id)
     user_info.append((myname, surname, email, birthday, address, postal_code, country, cellphone))

     total_discount = '%.2f' % 0
     total_price = pack_price
     
     return render_template('PackCheckout.html', is_logged_in=logged_in, clearance_level=clearance, credit=credit, user_info=user_info, subtotal=pack_price, discount=total_discount, total_price=total_price)

def finish_payment(pack_price):
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     credit = credit + pack_price
     update_credit(credit, user_id)

     payment_id = "211810"
     pay_type = "credit"
     mode = "online"
     receipt = "some_document"
     new_payment(user_id, None, payment_id, pay_type, mode, receipt)

     return redirect('/myWallet')

@payment.route('/CartCheckout', methods=['POST', 'GET'])
@requires_access_level(1)
def confirm_cart_payment():
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     if request.method == 'POST' and "confirm_payment" in request.form:
          return finish_pay()

     user_info = []
     myname, surname, email, birthday, address, postal_code, country, cellphone = list_user_info(user_id)
     user_info.append((myname, surname, email, birthday, address, postal_code, country, cellphone))

     cart_subtotal = get_my_cart_price(user_id, "ongoing") #Theres alot of elements missing in this function
     subtotal = sum([(x[0] * x[1]) for x in cart_subtotal])
     total_price = (get_my_cart_price(user_id, "ongoing")[0])[4]
     total_discount = round((((subtotal - total_price) / subtotal) * 100), 2)

     return render_template('Checkout.html', is_logged_in=logged_in, clearance_level=clearance, credit=credit, user_info=user_info, subtotal=subtotal, discount=total_discount, total_price=total_price)

def finish_pay():
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     cart_subtotal = get_my_cart_price(user_id, "ongoing") #Theres alot of elements missing in this function
     subtotal = sum([(x[0] * x[1]) for x in cart_subtotal])
     total_price = (get_my_cart_price(user_id, "ongoing")[0])[4]
     total_discount = round((((subtotal - total_price) / subtotal) * 100), 2)
     
     cart_info = user_cart_info(user_id, "ongoing")
     for user_id, cart_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status in cart_info:
          new_order(cart_id, user_id, product_id, product_qty, product_subtotal, product_discount, cart_price)
     
     payment_id = "211810"
     pay_type = "credit"
     mode = "online"
     receipt = "some_document"
     order_id = cart_id
     new_payment(user_id, order_id, payment_id, pay_type, mode, receipt)
     cart_id = (user_cart(user_id, "ongoing")[0])
     erase_cart("ordered", user_id, cart_id)

     return redirect('/myOrders')

#AdminControlPanel
@payment.route('/TheBrain/ManageOrders/ListOrders', methods=['GET'])
@requires_access_level(2)
def list_orders():
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     result = []
     orders = orders_list()

     for order_id, user_id, product_id, product_qty, title, vendor, status, created_at in orders:
          result.append((order_id, user_id, product_id, product_qty, title, vendor, status, created_at))

     return render_template("ListOrders.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

def bad_request_response(reason):
     '''
          FIXME: Put this in a utils.py
     '''
     response = jsonify({'reason': reason})
     response.status_code = http.HTTPStatus.BAD_REQUEST
     return response