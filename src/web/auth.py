"""
Code related to authentication

Login/Register endpoints
Authentication with Facebook/Google
"""

import http, time, requests, json

from functools import wraps
from flask import Flask, request, Blueprint, Response, jsonify, session, render_template, redirect, url_for

from src.use_cases.register import register_login, get_user_id, get_user_info
from src.use_cases.user import get_user_from_id, insert_profile
from src.use_cases.login import login as verify_login
from src.web.validator import name_validator, email_validator, password_validator
from src import config
from flask_mail import Mail, Message
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from src.use_cases.auth_util import hash_password
from src.adapter.users_repository import database_users
from src.use_cases.login import PasswordAlreadyExistsException
from src.use_cases.user import change_password, get_user_from_id

app = Flask('Kappy')
auth = Blueprint('auth', __name__, template_folder='templates')
SECRET_KEY = config.SECRET_KEY
app.config.update(dict(
    MAIL_SERVER = config.MAIL_SERVER,
    MAIL_PORT = config.MAIL_PORT,
    MAIL_USERNAME = config.MAIL_USERNAME,
    MAIL_PASSWORD = config.MAIL_PASSWORD,
    MAIL_USE_TLS = config.MAIL_USE_TLS,
    MAIL_USE_SSL = config.MAIL_USE_SSL,
))
mail = Mail(app)

@auth.before_request
def make_session_permanent():
    session.permanent = True  #Session lasts 30 days

def logged_out_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" in session:
            logged_in = True
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                return redirect('/Login')

            user_id = get_user_id(session['user'])[0]
            clearance = get_user_from_id(user_id)[1]
            if not clearance >= access_level:
                return redirect('/')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_vars(session):
    if "user" in session:
        logged_in = True
        myname = get_user_info(session['user'])[0]
        credit = get_user_info(session['user'])[1]
        user_id = get_user_id(session['user'])[0]
        clearance = get_user_from_id(user_id)[1]
    else:
        logged_in = False
        myname = ''
        credit = 0
        user_id = None
        clearance = 0

    return logged_in, myname, credit, user_id, clearance

@auth.route('/Login', methods=['POST', 'GET'])
@logged_out_required
def loginpage():
    form = request.form
    if request.method == 'POST' and "resetpw_email" in request.form:
        recipient_email = request.form['resetpw_email']
        s = Serializer(SECRET_KEY, 1800)
        token = s.dumps(recipient_email).decode('utf-8')
        msg = Message('Kappy - Reset Password Request', sender =  ("Kappy - Security", 'geral@kappy.pt'), recipients = [recipient_email])
        msg.body = f'''Hey kind sir, sending you this email in order for you to reset your password, please click the link below:
                    {url_for('.reset_token', token=token, _external=True)}
                    '''
        mail.connect()
        mail.send(msg)
        return redirect('/ResetConfirm')
    return render_template('AuthForms.html')

    if 'resetpw_email' in form:
        if not email_validator(form['resetpw_email']):
            return bad_request_response('Invalid email')
    else:
        return bad_request_response('Missing email field')

@auth.route('/ResetConfirm', methods=['GET'])
def reset_link_sent():
    return render_template('ResetConfirm.html')

@auth.route('/reset_password/<token>', methods=['POST', 'GET'])
def reset_token(token):
    form = request.form
    s = Serializer(SECRET_KEY, 1800)
    if request.method == 'POST' and "new_password" in request.form:
            email, hashed_password, salt = database_users.get_user(s.loads(token))
            provided_password = request.form['new_password']
            password = hash_password(provided_password, salt)
            if password == hashed_password:
                raise PasswordAlreadyExistsException(password)
            else:
                change_password(password, email)
                return redirect ('/Login')

    return render_template('ResetPassword.html')

    if 'new_password' in form:
        if not password_validator(form['new_password']):
            return bad_request_response('Invalid password')
    else:
        return bad_request_response('Missing password field')

@auth.route('/LoggingIn', methods=['POST'])
def login():
    form = request.form

    if form is None or len(form) != 3:
        return bad_request_response('Invalid number of arguments')

    if 'email' in form:
        if not email_validator(form['email']):
            return bad_request_response('Invalid email')
    else:
        return bad_request_response('Missing email field')

    if 'password' in form:
        if not password_validator(form['password']):
            return bad_request_response('Invalid password')
    else:
        return bad_request_response('Missing password field')

    if session.get('user') is not None:
        return bad_request_response('You are already logged in')

    logged_in = verify_login(form['email'].lower(), form['password'])
    session['user'] = form['email'].lower()
    return redirect('/')

    # return bad_request_response('Login not Sucessfull') - make this on the template not here, and make it pretty!

@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@auth.route('/Registration', methods=['POST'])
def register():
    form = request.form

    if form is None or len(form) != 5:
        return bad_request_response('Invalid number of arguments')

    if 'myName' in form:
        if not name_validator(form['myName']):
            return bad_request_response('Invalid first name')
    else:
        return bad_request_response('Missing first name field')

    if 'Surname' in form:
        if not name_validator(form['Surname']):
            return bad_request_response('Invalid last name')
    else:
        return bad_request_response('Missing lastname field')

    if 'email' in form:
        if not email_validator(form['email']):
            return bad_request_response('Invalid email')
    else:
        return bad_request_response('Missing email field')

    if 'password' in form:
        if not password_validator(form['password']):
            return bad_request_response('Invalid password')
    else:
        return bad_request_response('Missing password field')

    if session.get('user') is not None:
        return bad_request_response('You are already logged in')

    email = form['email'].lower()
    password = form['password']
    myname = form['myName']
    surname = form['Surname']

    if register_login(email, password, myname, surname):
        session['user'] = form['email'].lower()     #Creates a session on the website      
        user_id = get_user_id(email)[0]
        insert_profile(user_id)
        webhook_url = 'https://discord.com/api/webhooks/1005591658575954082/r_dhP2wzrhpicG_aDWiVp9KRA_VPXbQDo399lGpHyTiECS7XS1rWA1uOW7iGGwGJm94m'
        data = { 'content': f'Um novo registo foi efetuado com sucesso! Bem-vindo {myname} {surname}!' }
        r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        
        return redirect('/')
    else:
        return redirect('/Login')

def bad_request_response(reason):
    response = jsonify({'reason': reason})
    response.status_code = http.HTTPStatus.BAD_REQUEST
    return response
