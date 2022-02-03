import http

from functools import wraps
from flask import request, Blueprint, Response, jsonify, session, render_template, redirect
from src.use_cases.user import get_user, get_user_from_id, delete_user, update_info, change_password, list_users, list_user_info
from src.use_cases.register import get_user_info, get_user_id
from src.use_cases.user import get_user_from_id, manage_clearance
from src.use_cases.auth_util import hash_password
from src.use_cases.login import PasswordNotFoundException
from src.web.validator import name_validator, postal_code_validator, email_validator, password_validator, address_validator, cellphone_validator
from src.web.auth import requires_access_level

user = Blueprint('user', __name__, template_folder='templates')

@user.route('/myAccount', methods=['POST', 'GET'])
@requires_access_level(1)
def myAccount():
    if "user" in session:
        logged_in = True
        myname, credit = get_user_info(session['user'])
        user_id = get_user_id(session['user'])[0]
        clearance = get_user_from_id(user_id)[1]
        myname, surname, email, birthday, address, postal_code, country, cellphone = list_user_info(user_id)
        print(repr(list_user_info(user_id)))
    else:
        myname = ''
        credit = 0
        logged_in = False
        clearance = 0

    return render_template('myAccount.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, myname=myname, surname=surname, email=email, birthday=birthday, address=address, postal_code=postal_code, country=country, cellphone=cellphone)


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

    if 'postal_code' in form:
        if not postal_code_validator(form['postal_code']) and not form['postal_code'] == '':
            return bad_request_response('Invalid postal code')

    if 'address' in form:
        if not address_validator(form['address']) and not form['address'] == '':
            return bad_request_response('Invalid address')

    if 'cellphone' in form:
        if not cellphone_validator(form['cellphone']) and not form['cellphone'] == '':
            return bad_request_response('Invalid cellphone')

    if 'password_del' in form:
        if not password_validator(form['password_del']):
            return bad_request_response('Invalid password')

    if 'password_chg' in form:
        if not password_validator(form['password_chg']):
            return bad_request_response('Invalid password')

    if 'password_new' in form:
        if not password_validator(form['password_new']):
            return bad_request_response('Invalid password')

    if "user" in session:
        logged_in = True
        myname, credit = get_user_info(session['user'])
        user_id = get_user_id(session['user'])[0]
        clearance = get_user_from_id(user_id)[1]
        email, hashed_password, salt = get_user(session['user'])
        if request.method == 'POST' and "password_del" in form:
            provided_password = form['password_del']
            password = hash_password(provided_password, salt)
            if password == hashed_password:
                delete_user(user_id, password)
                return redirect('/logout') #FIXME: User logs out by doing Post even if the pw is wrong
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
            postal_code = form['postal_code']
            address = form['address']
            birthday = form['birthday']
            country = form['country']
            cellphone = form['cellphone']
            info_list = [myname, surname, email, birthday, address, postal_code, country, cellphone]
            conv = lambda i : i or None
            res = [conv(i) for i in info_list]
            myname = res[0]
            surname = res[1]
            email = res[2]
            birthday = res[3]
            address = res[4]
            postal_code = res[5]
            country = res[6]
            cellphone = res[7]
            update_info(myname, surname, email, birthday, address, postal_code, country, cellphone, user_id)
            email = get_user_from_id(user_id)[0]
            session['user'] = email
            return redirect('/myAccount')
    else:
        myname = ''
        credit = 0
        logged_in = False
        clearance = 0

    return redirect('/myAccount')

#AdminControlPanel
@user.route('/TheBrain/UserData', methods=['GET'])
@requires_access_level(2)
def lists_events():
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
    users = list_users()

    for user_id, email, credit, myname, surname, postal_code, address, city, country, birthday, cellphone, created_at in users:
        result.append((user_id, email, credit, myname, surname, postal_code, address, city, country, birthday, cellphone, created_at))

    return render_template("UserList.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)


@user.route('/change_role', methods=['POST'])
@requires_access_level(2)
def manage_roles():
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

    chosen_user_id = request.form['user_id']
    clearance_number = request.form['clearance_level']
    manage_clearance(clearance_number, chosen_user_id)

    return render_template("Roles.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit)

def bad_request_response(reason):
    response = jsonify({'reason': reason})
    response.status_code = http.HTTPStatus.BAD_REQUEST
    return response