import http, datetime

from functools import wraps
from flask import request, Blueprint, Response, jsonify, session, render_template, redirect
from decimal import *
from src.use_cases.user import get_user, get_user_from_id, delete_account, update_info, change_password, list_users, delete_user, list_user_info, update_outlay
from src.use_cases.user import get_user_from_id, manage_clearance, user_profile, new_address, get_user_addresses, get_user_address, update_address, update_shipping, update_billing, delete_address
from src.use_cases.auth_util import hash_password
from src.use_cases.login import PasswordNotFoundException
from src.use_cases.orders import total_spent
from src.web.validator import name_validator, postal_code_validator, email_validator, password_validator, address_validator, cellphone_validator
from src.web.auth import requires_access_level, log_vars
from src.web.product import show_cart

user = Blueprint('user', __name__, template_folder='templates')

@user.route('/myAccount', methods=['POST', 'GET'])
@requires_access_level(1)
def myAccount():
    logged_in, myname, credit, user_id, clearance = log_vars(session)
    myname, surname, email, birthday = list_user_info(user_id)

    result, addresslist = [], []
    user_id, user_class, class_milestone, class_expiration, class_days, money_spent, credits_bought, credits_spent, bought_prod_qty, bought_sil_box, bought_gol_box, bought_dia_box, reviews_made, created_at = user_profile(user_id)
    money_list = total_spent(user_id)
    credits_bought = Decimal('0.0')
    money_spent = Decimal('0.0')
    credits_spent = Decimal('0.0')
    for money in money_list:
        money_spent += money[1]
        if money[0] == None:
            credits_bought += money[1]
    credits_spent = credits_bought - credit 
    new_milestone = money_spent // 3000
    if new_milestone > class_milestone:
        user_class = 1
        class_days = class_days + 40
        class_milestone = new_milestone
        if class_days > 0:
            class_expiration = datetime.datetime.now() + datetime.timedelta(days=class_days)
    else:
        class_days = (class_expiration - datetime.datetime.now()).days
    update_outlay(user_class, class_milestone, class_expiration, class_days, money_spent, credits_bought, credits_spent, user_id)
    class_expiration = class_expiration.strftime("%d/%m/%Y às %H:%M")
    progress_bar = (money_spent / 3000)
    progress_bar = (progress_bar - int(progress_bar)) * 100
    result.append((user_class, class_milestone, progress_bar, class_expiration, class_days, money_spent, int(credits_bought), credits_spent, bought_prod_qty, bought_sil_box, bought_gol_box, bought_dia_box, reviews_made))

    cart_products, cart_price, cart_id = show_cart(user_id)

    address_qty = len(get_user_addresses(user_id))
    addresses = get_user_addresses(user_id)

    for address in addresses:
        user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing = address[:12]
        addresslist.append((user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing))

    return render_template('myAccount.html', user_id=user_id, is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id, myname=myname, surname=surname, email=email, birthday=birthday, result=result, address_qty=address_qty, addresslist=addresslist)

@user.route('/UpdatingInfo', methods=['POST', 'GET'])
@requires_access_level(1)
def UpdatingInfo():
    form = request.form
    if 'myname' in form:
        if not name_validator(form['myname']) and not form['myname'] == '':
            return bad_request_response('Invalid first name')

    if 'surname' in form:
        if not name_validator(form['surname']) and not form['surname'] == '':
            return bad_request_response('Invalid last name')

    if 'email' in form:
        if not email_validator(form['email']) and not form['email'] == '':
            return bad_request_response('Invalid email')

    if 'password_del' in form:
        if not password_validator(form['password_del']):
            return bad_request_response('Invalid password')

    if 'password_chg' in form:
        if not password_validator(form['password_chg']):
            return bad_request_response('Invalid password')

    if 'password_new' in form:
        if not password_validator(form['password_new']):
            return bad_request_response('Invalid password')

    logged_in, myname, credit, user_id, clearance = log_vars(session)
    email, hashed_password, salt = get_user(session['user'])

    if request.method == 'POST' and "password_del" in form:
        provided_password = form['password_del']
        password = hash_password(provided_password, salt)
        if password == hashed_password:
            delete_account(user_id, password)
            return redirect('/logout')
        else:
            raise PasswordNotFoundException(provided_password)
    elif request.method == 'POST' and "password_chg" in form:
        provided_password = form['password_chg']
        password = hash_password(provided_password, salt)
        if password == hashed_password:
            new_provided_password = form['password_new']
            new_password = hash_password(new_provided_password, salt)
            change_password(new_password, email)
            return redirect('/myAccount')
        else:
            raise PasswordNotFoundException(provided_password)
    elif request.method == 'POST' and "email" in form:
        myname = form['myname']
        surname = form['surname']
        email = form['email'].lower()
        birthday = form['birthday']
        info_list = [myname, surname, email, birthday]
        conv = lambda i : i or None
        res = [conv(i) for i in info_list]
        myname = res[0]
        surname = res[1]
        email = res[2]
        birthday = res[3]
        update_info(myname, surname, email, birthday, user_id)
        email = get_user_from_id(user_id)[0]
        session['user'] = email
        return redirect('/myAccount')

    return redirect('/myAccount')

@user.route('/myAddress', methods=['POST', 'GET'])
@requires_access_level(1)
def myAddress():
    logged_in, myname, credit, user_id, clearance = log_vars(session)
    cart_products, cart_price, cart_id = show_cart(user_id)
    address_qty = len(get_user_addresses(user_id))

    if address_qty >= 3:
        return redirect('/myAccount')

    if request.method == 'POST' and "save_address" in request.form:
        return insert_address(user_id)

    return render_template('myAddress.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id)

def insert_address(user_id):
    form = request.form

    address_name = form['address_name']
    full_name = form['full_name']
    address = form['address']
    postal_code = form['postal_code']
    city = form['city']
    country = "Portugal"
    phone_number = form['phone_number']
    fiscal_number = form['fiscal_number']
    main_shipping = form.get('main_check')
    main_billing = form.get('fiscal_check')

    if main_shipping == "on":
        main_shipping = True
        update_shipping(False, user_id)
    else:
        main_shipping = False

    if main_billing == "on":
        main_billing = True
        update_billing(False, user_id)
    else:
        main_billing = False


    new_address(user_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing)

    return redirect('/myAccount')

@user.route('/del_address/<int:user_id>/<int:address_id>', methods=['POST', 'GET'])
def remove_address(user_id, address_id):
    
    delete_address(user_id, address_id)

    return redirect(request.referrer)

@user.route('/edit_address/<int:user_id>/<int:address_id>', methods=['POST', 'GET'])
def change_address(user_id, address_id):
    logged_in, myname, credit, user_id, clearance = log_vars(session)
    cart_products, cart_price, cart_id = show_cart(user_id)
    form = request.form

    address_info = []
    user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing = get_user_address(user_id, address_id)[:12]
    address_info.append((user_id, address_id, address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing))

    if request.method == 'POST' and "address_name" in request.form:
        address_name = form['address_name']
        full_name = form['full_name']
        address = form['address']
        postal_code = form['postal_code']
        city = form['city']
        country = form['country']
        phone_number = form['phone_number']
        fiscal_number = form['fiscal_number']
        main_shipping = form.get('main_check')
        main_billing = form.get('fiscal_check')
        info_list = [address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing]
        conv = lambda i : i or None
        res = [conv(i) for i in info_list]
        address_name = res[0]
        full_name = res[1]
        address = res[2]
        postal_code = res[3]
        city = res[4]
        country = res[5]
        phone_number = res[6]
        fiscal_number = res[7]
        main_shipping = res[8]
        main_billing = res[9]

        if main_shipping == "on":
            main_shipping = True
            update_shipping(False, user_id)
        else:
            main_shipping = False

        if main_billing == "on":
            main_billing = True
            update_billing(False, user_id)
        else:
            main_billing = False

        update_address(address_name, full_name, address, postal_code, city, country, phone_number, fiscal_number, main_shipping, main_billing, user_id, address_id)

        return redirect('/myAccount')

    return render_template('myAddress.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cart_products=cart_products, cart_price=cart_price, cart_id=cart_id, address_info=address_info)


#AdminControlPanel
@user.route('/TheBrain/ManageUsers/UserList', methods=['GET'])
@requires_access_level(2)
def lists_products():
    logged_in, myname, credit, user_id, clearance = log_vars(session)

    result = []
    users = list_users()

    for user_id, email, credit, myname, surname, birthday, created_at in users:
        result.append((user_id, email, credit, myname, surname, birthday, created_at))

    return render_template("UserList.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

#AdminControlPanel
@user.route('/TheBrain/ManageUsers/EditUser', methods=['POST', 'GET'])
@requires_access_level(2)
def edit_user():
    logged_in, myname, credit, user_id, clearance = log_vars(session)
    form = request.form

    if request.method == 'POST' and "user_id" in form:
        cuser_id = form['user_id']
        cmyname, csurname, cemail, cbirthday = list_user_info(cuser_id)
        return render_template("EditUser.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, cuser_id=cuser_id, cmyname=cmyname, csurname=csurname, cemail=cemail, cbirthday=cbirthday)

    return render_template("EditUser.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

@user.route('/Updating_UserInfo', methods=['POST', 'GET'])
@requires_access_level(1)
def Updating_UserInfo():
    form = request.form
    if 'myname' in form:
        if not name_validator(form['myname']) and not form['myname'] == '':
            return bad_request_response('Invalid first name')

    if 'surname' in form:
        if not name_validator(form['surname']) and not form['surname'] == '':
            return bad_request_response('Invalid last name')

    if 'email' in form:
        if not email_validator(form['email']) and not form['email'] == '':
            return bad_request_response('Invalid email')

    if request.method == 'POST' and "email" in form:
        cmyname = form['myname']
        csurname = form['surname']
        cemail = form['email'].lower()
        cbirthday = form['birthday']
        info_list = [cmyname, csurname, cemail, cbirthday]
        conv = lambda i : i or None
        res = [conv(i) for i in info_list]
        cmyname = res[0]
        csurname = res[1]
        cemail = res[2]
        cbirthday = res[3]
        cuser_id = form['user_id'] #FIXME Find out how to remove the extra user_id input
        update_info(cmyname, csurname, cemail, cbirthday, cuser_id)
        return redirect('/TheBrain/ManageUsers/EditUser')

    return redirect('/TheBrain/ManageUsers/EditUser')

#AdminControlPanel
@user.route('/erase_user', methods=['POST'])
@requires_access_level(2)
def erase_user():
    user_id = request.form['user_id']
    delete_user(user_id)
    return redirect('/TheBrain')

#AdminControlPanel
@user.route('/change_role', methods=['POST'])
@requires_access_level(2)
def manage_roles():
    logged_in, myname, credit, user_id, clearance = log_vars(session)

    chosen_user_id = request.form['user_id']
    clearance_number = request.form['clearance_level']
    manage_clearance(clearance_number, chosen_user_id)

    return render_template("Roles.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

def bad_request_response(reason):
    response = jsonify({'reason': reason})
    response.status_code = http.HTTPStatus.BAD_REQUEST
    return response