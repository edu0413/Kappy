"""
Code related to the payment
"""
import http, requests, json
from flask import Blueprint, render_template, redirect, jsonify, request, session, url_for, abort
from src.use_cases.orders import new_order, orders_list, new_payment
from src.use_cases.carts import user_cart, get_my_cart_price, erase_cart, user_cart_info
from src.use_cases.register import update_credit
from src.use_cases.user import list_user_info, get_user_addresses
from src.web.auth import requires_access_level, log_vars
from src.web.product import show_cart
from decimal import *

payment = Blueprint('payment', __name__, template_folder='templates')

''' #Not included in the beginning
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
          packbilling_addressid = request.form['chosen_ba']
          print(packbilling_addressid)
          return finish_payment(pack_price, packbilling_addressid)

     user_addresses = []
     addresses = get_user_addresses(user_id)

     for address in addresses:
          user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing = address[:12]
          user_addresses.append((user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing))

     total_discount = '%.2f' % 0
     total_price = pack_price
     
     return render_template('PackCheckout.html', is_logged_in=logged_in, clearance_level=clearance, credit=credit, user_addresses=user_addresses, subtotal=pack_price, discount=total_discount, total_price=total_price)

def finish_payment(pack_price, packbilling_addressid):
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     
     credit = credit + pack_price
     update_credit(credit, user_id)

     payment_id = "211810"
     pay_type = "credit"
     mode = "online"
     receipt = "some_document"
     new_payment(user_id, None, packbilling_addressid, payment_id, pack_price, pay_type, mode, receipt)

     return redirect('/myWallet')
'''
''''''
@payment.route('/CartCheckout', methods=['POST', 'GET'])
@requires_access_level(1)
def confirm_cart_payment():
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     if request.method == 'POST' and "confirm_payment" in request.form:
          shipping_addressid = request.form['chosen_sa']
          billing_addressid = request.form['chosen_ba']
          return finish_pay(shipping_addressid, billing_addressid)

     if request.method == 'POST' and "confirm_mbway_payment" in request.form:
          shipping_addressid = request.form['chosen_sa']
          billing_addressid = request.form['chosen_ba']
          return mbway_payment(shipping_addressid, billing_addressid)

     

     user_addresses = []
     addresses = get_user_addresses(user_id)

     for address in addresses:
          user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing = address[:12]
          user_addresses.append((user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing))

     cart_subtotal = get_my_cart_price(user_id, "ongoing") #Theres alot of elements missing in this function
     subtotal = sum([(x[0] * x[1]) for x in cart_subtotal])
     total_price = (get_my_cart_price(user_id, "ongoing")[0])[4]
     total_discount = round((((subtotal - total_price) / subtotal) * 100), 2)
     return render_template('Checkout.html', is_logged_in=logged_in, clearance_level=clearance, credit=credit, user_addresses=user_addresses, subtotal=subtotal, discount=total_discount, total_price=total_price)

def finish_pay(shipping_addressid, billing_addressid):
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     cart_subtotal = get_my_cart_price(user_id, "ongoing") #Theres alot of elements missing in this function
     subtotal = sum([(x[0] * x[1]) for x in cart_subtotal])
     total_price = (get_my_cart_price(user_id, "ongoing")[0])[4]
     total_discount = round((((subtotal - total_price) / subtotal) * 100), 2)
     
     cart_info = user_cart_info(user_id, "ongoing")
     for user_id, cart_id, product_id, product_title, product_qty, product_subtotal, product_discount, product_total, cart_price, status in cart_info:
          new_order(cart_id, user_id, shipping_addressid, product_id, product_qty, product_subtotal, product_discount, cart_price)
     
     payment_id = "211810"
     pay_type = "credit"
     mode = "online"
     receipt = "some_document"
     order_id = cart_id
     new_payment(user_id, order_id, billing_addressid, payment_id, cart_price, pay_type, mode, receipt)
     cart_id = (user_cart(user_id, "ongoing")[0])
     erase_cart("ordered", user_id, cart_id)

     return redirect('/myOrders')

def mbway_payment(shipping_addressid, billing_addressid):
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     cart_subtotal = get_my_cart_price(user_id, "ongoing") #Theres alot of elements missing in this function
     subtotal = sum([(x[0] * x[1]) for x in cart_subtotal])
     total_price = (get_my_cart_price(user_id, "ongoing")[0])[4]
     total_discount = round((((subtotal - total_price) / subtotal) * 100), 2)
     
     mbway_phone = request.form['cellphone']
     total_price = str(total_price)

     url = "https://sandbox.eupago.pt/clientes/rest_api/mbway/create"

     payload = {
          "chave": "demo-8a44-d896-e292-cd5",
          "valor": total_price,
          "alias": mbway_phone
     }
     headers = {
          "Accept": "application/json",
          "Content-Type": "application/json"
     }
     print(payload)
     response = requests.post(url, json=payload, headers=headers)
     print(response.text)

     if request.method == 'POST' and "go_to_orders" in request.form:
          return redirect ('/myOrders')


     return render_template('SucessfullPayment.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)


@payment.route('/webhook', methods=['POST'])
def webhook():
     if request.method == 'POST':
          print(request.json)
          webhook_url = 'https://discord.com/api/webhooks/1001975186695925770/NDFvftZaOEL7FnbV_7q6oe1EuqtDrTyaGTIEwhcpOItRifOiCOv4lzp8QbegHz0ROAZW'
          data = { 'content': 'This is my first time webhooking!' }
          r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
          return 'success', 200
     else:
          abort(400)

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