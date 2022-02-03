"""
Code related to the payment
"""
import http
from flask import Blueprint, render_template, redirect, jsonify, request, session, url_for
from src.use_cases.orders import new_order, orders_list
from src.use_cases.register import get_user_info, get_user_id, update_credit
from src.use_cases.user import get_user_from_id
from src.web.auth import requires_access_level

payment = Blueprint('payment', __name__, template_folder='templates')

@payment.route('/myWallet', methods=['POST', 'GET'])
def carteira():
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
          qty_bought = 1

          if request.method == 'POST' and "SmallestPack" in request.form:
               sell_product_price, total_price = 5, 5
               product_heading = "Mão de Feijões"
               return redirect(url_for('.confirm_payment', qty_bought=qty_bought, sell_product_price=sell_product_price, product_heading=product_heading, total_price=total_price, **request.args))
          
          elif request.method == 'POST' and "SmallPack" in request.form:
               sell_product_price, total_price = 10, 10
               product_heading = "Saquinho de Feijões"
               return redirect(url_for('.confirm_payment', qty_bought=qty_bought, sell_product_price=sell_product_price, product_heading=product_heading, total_price=total_price, **request.args))
          
          elif request.method == 'POST' and "MediumPack" in request.form:
               sell_product_price, total_price = 20, 20
               product_heading = "Taça de Feijões"
               return redirect(url_for('.confirm_payment', qty_bought=qty_bought, sell_product_price=sell_product_price, product_heading=product_heading, total_price=total_price, **request.args))
          
          elif request.method == 'POST' and "BigPack" in request.form:
               sell_product_price, total_price = 50, 50
               product_heading = "Saca de Feijões"
               return redirect(url_for('.confirm_payment', qty_bought=qty_bought, sell_product_price=sell_product_price, product_heading=product_heading, total_price=total_price, **request.args))
          
          elif request.method == 'POST' and "BiggestPack" in request.form:
               sell_product_price, total_price = 100, 100
               product_heading = "Caixa de Feijões"
               return redirect(url_for('.confirm_payment', qty_bought=qty_bought, sell_product_price=sell_product_price, product_heading=product_heading, total_price=total_price, **request.args))
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0

     return render_template('myWallet.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

@payment.route('/Checkout', methods=['POST', 'GET'])
def confirm_payment():
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
          event_id = request.args.get('event_id')
          qty_bought = request.args.get('qty_bought')
          sell_product_price = request.args.get('sell_product_price')
          product_heading = request.args.get('product_heading')
          total_price = request.args.get('total_price')
          if request.method == 'POST' and product_heading in {'Mão de Feijões', 'Saquinho de Feijões', 'Taça de Feijões', 'Saca de Feijões', 'Caixa de Feijões'}:
               credit = int(credit)
               credit = credit + int(sell_product_price)
               update_credit(credit, user_id)
               return finish_pay(qty_bought, sell_product_price, product_heading, total_price)
          elif request.method == 'POST' and product_heading not in {'Mão de Feijões', 'Saquinho de Feijões', 'Taça de Feijões', 'Saca de Feijões', 'Caixa de Feijões'}:
               order_id = new_order(user_id, event_id, qty_bought)
               return finish_pay(qty_bought, sell_product_price, product_heading, total_price)
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0

     return render_template('Checkout.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

@payment.route('/Paying', methods=['POST', 'GET'])     
def finish_pay(qty_bought, sell_product_price, product_heading, total_price):
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
     else:
          myname = ''
          credit = 0
          logged_in = False

     return redirect(url_for('.paid'))

@payment.route('/AuthPayment', methods=['POST', 'GET'])
def paid():
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
          if request.method == 'POST':
               return redirect('/')
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0

     return render_template('SucessfullPayment.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

#AdminControlPanel
@payment.route('/TheBrain/UserOrders', methods=['GET'])
@requires_access_level(2)
def list_orders():
     if "user" in session:
          logged_in = True
          myname, credit = get_user_info(session['user'])
          user_id = get_user_id(session['user'])[0]
          clearance = get_user_from_id(user_id)[1]
    
     else:
          myname = ''
          credit = 0
          logged_in = False
          clearance = 0

     result = []
     orders = orders_list()

     for order_id, user_id, event_id, product_heading, qty_bought, status, created_at in orders:
          result.append((order_id, user_id, event_id, product_heading, qty_bought, status, created_at))

     return render_template("UserOrders.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

def bad_request_response(reason):
     '''
          FIXME: Put this in a utils.py
     '''
     response = jsonify({'reason': reason})
     response.status_code = http.HTTPStatus.BAD_REQUEST
     return response