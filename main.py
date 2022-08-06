"""

Flask App (sessions key, run app, general configurations)
Endpoint paths
Control Panel endpoint
Error Handlers here?

"""
import os
from flask import Flask, send_from_directory, session, render_template, jsonify, request
from src.web.auth import *
from src.web.product import *
from src.web.user import *
from src.web.payment import *
from src.web.products_list import *
from src.config import *
from src.use_cases.lootbox import publish_lootbox, get_loot_ids, lootbox_items, get_lootbox, get_inv_ids, inventory_items
from src.use_cases.register import update_credit
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_sitemapper import Sitemapper

app = Flask('Kappy')
csrf = CSRFProtect(app)
sitemapper = Sitemapper(app)
app.register_blueprint(auth) # Register authentication endpoints
app.register_blueprint(product) # Register everything about the seller (sell/products)
app.register_blueprint(user) # Register additional user details
app.register_blueprint(payment) # Payment functionalities
app.register_blueprint(products_list)
app.secret_key = config.SECRET_KEY
app.config["SERVER_NAME"] = "kappy.pt"#CHANGE BACK to kappy.pt
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['ENV'] = 'production'#CHANGE BACK TO production
app.config['DEBUG'] = False #CHANGE BACK TO False
# Set secret key for authenticated cookies

sitemapper.add_endpoint("auth.loginpage", changefreq="monthly", priority="0.9")
sitemapper.add_endpoint("products_list.index", changefreq="daily", priority="1")

@app.route("/sitemap.xml")
def kappy_sitemap():
	return sitemapper.generate()

@app.route('/assets/<path:path>') #Study this and see what it does exactly
def send_static(path):
     curr_path = os.getcwd()
     return send_from_directory(os.path.join(curr_path, 'templates', 'assets'), path)

@app.route("/user/<path:filename>")
def footer_pages(filename):
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     print(filename)

     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

#Admin
@app.route("/TheBrain/ManageLootbox/CreateLootbox")
@requires_access_level(2)
def create_lootbox():
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     if request.method == 'POST' and "lootbox_prod[]" in request.form:#CHECK THIS, SOMETHING IS WRONG
          return register_lootbox()

     return render_template('CreateLootbox.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

@app.errorhandler(404) #Exception instead of 404 for when its not specific
def ErrorPage_404(e):
     return render_template('Error404.html')

@app.errorhandler(500) #Exception instead of 500 for when its not specific
def ErrorPage_500(e):
     return render_template('Error500.html')

@app.errorhandler(CSRFError) #Exception instead of bad request csrf not valid for when its not specific
def handle_csrf_error(e):
     session.pop('user', None)
     return redirect('/Login')

@app.route('/TheBrain')
@requires_access_level(2)
def control_panel():
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template('ControlPanel.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

@app.route("/TheBrain/<path:filename>")
@requires_access_level(2)
def admin_path(filename):
     logged_in, myname, credit, user_id, clearance = log_vars(session)

     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

@app.route("/TheBrain/ManageProducts/<path:filename>")
@requires_access_level(2)
def manage_products(filename):
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     
     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

@app.route("/TheBrain/ManageUsers/<path:filename>")
@requires_access_level(2)
def manage_users(filename):
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     
     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

@app.route("/TheBrain/ManageReviews/<path:filename>")
@requires_access_level(2)
def manage_reviews(filename):
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     
     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template(filename + '.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

    # Flask already assumes the artifacts are inside the template/ folder

''' #Not included in the beginning
@app.route("/register_lootbox", methods=['POST'])
@requires_access_level(2)
def register_lootbox():
     user_id = get_user_id(session['user'])[0]
     #FIXME - Introduce conditionals like, only one product id per box, total chances need to sum to 100
     form = request.form
     params = ('lootbox_id', 'lootbox_prod[]', 'lootbox_chance[]')

     if form is None:
          return bad_request_response('Invalid number of arguments')

     for param in params:
          if param not in form:
               return bad_request_response(f'I need a {param} parameter')

     product_id = form.getlist('lootbox_prod[]')
     product_id = [int(x) for x in product_id]
     if len(product_id) != len(set(product_id)):
          return bad_request_response('You cannot repeat the product more than once, please pay attention!')

     chances = form.getlist('lootbox_chance[]')
     chances = [int(x) for x in chances]
     if sum(chances) != 100:
          return bad_request_response('The chances sum need to be 100, this is math!')

     lootbox_id = form['lootbox_id']
     lootbox_id = [int(x) for x in lootbox_id]
     lootbox_id = lootbox_id * len(product_id)

     lootbox_list = (list(zip(lootbox_id, product_id, chances)))

     publish_lootbox(lootbox_list)
     return redirect('/KappyBox')


@app.route("/KappyBox", methods=['POST', 'GET'])
@requires_access_level(1)
def kappy_box():
     logged_in, myname, credit, user_id, clearance = log_vars(session)
     
     loot_ids = get_loot_ids()
     lootbox_prods = []

     for lootbox_id, product_id in loot_ids:
          lootbox_id, category, product_id, image, title, chances = lootbox_items(lootbox_id, product_id)
          for file in os.listdir(image):
               image = file 
          lootbox_prods.append((lootbox_id, category, product_id, image, title, chances))

     if request.method == 'POST' and "buy_lootbox" in request.form:
          return buy_box(lootbox_id)

     inventory_ids = get_inv_ids(user_id)
     lootbox_inv = []

     for inventory_id in inventory_ids:
          inventory_id, lootbox_id, category, product_id, image, title, chances, active = inventory_items(inventory_id)
          for file in os.listdir(image):
               image = file 
          lootbox_inv.append((inventory_id, lootbox_id, category, product_id, image, title, chances, active))

     inventory_qty = len(lootbox_inv)
     cart_products, cart_price, cart_id = show_cart(user_id)

     return render_template('Lootbox.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, lootbox_prods=lootbox_prods, lootbox_inv=lootbox_inv, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id, inventory_qty=inventory_qty)

def buy_box(lootbox_id):
     user_id, credit = get_user_id(session['user'])
     loot_lists, loot_list, loot_chances = [], [], []
     loot_lists = get_loot_ids()
     price_tag = int(request.form['buy_lootbox'])

     if price_tag == 150 and credit >= 150:
          credit = credit - price_tag
          update_credit(credit, user_id)
     elif price_tag == 300 and credit >= 300:
          credit = credit - price_tag
          update_credit(credit, user_id)
     elif price_tag == 500 and credit >= 500:
          credit = credit - price_tag
          update_credit(credit, user_id)
     else:
          bad_request_response('Not enough Kappy Coins')

     for lootbox_id, product_id in loot_lists:
          lootbox_id, category, product_id, image, title, chances = lootbox_items(lootbox_id, product_id)
          loot_chances.append((chances))
          loot_list.append((product_id))

     product_id = str(random.choices(loot_list, weights=((loot_chances)), k=1))[1:-1]
     print(product_id)
     get_lootbox(user_id, lootbox_id, product_id)

     return redirect('/KappyBox')
'''

if __name__ == "__main__":
     hostname = os.getenv('HOSTNAME')
     port = os.getenv('PORT')
     app.run(host=config.flask_host, port=port)  # This blocks here