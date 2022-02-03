"""
Code related to the event functionality
"""

import os, http, time, random
from flask import Flask, Blueprint, render_template, redirect, jsonify, request, session, url_for
from src.use_cases.events import get_all_params, publish_event, update_perc, end_event, update_event, delete_event, list_events
from src.use_cases.customers import if_engaged, buy_ticket, subscribe_again, tickets_amount, get_participants, subs_list
from src.use_cases.orders import new_order
from src.use_cases.register import get_user_info, get_user_id, update_credit
from src.use_cases.user import get_user_from_id
from src.web.auth import requires_access_level
from datetime import date, datetime
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from src import config

event = Blueprint('event', __name__, template_folder='templates')

#Private API
@event.route('/Endgame')   #Should i put clearance decorator here?
def endgame(event_id):
    event_id, image, description, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(event_id)
    CustomerList, TicketList = zip(*[(x[0], x[1]) for x in get_participants(event_id)])
    Total_Tickets_Bought = sum(TicketList)
    if Total_Tickets_Bought == 0:
        winner_id = None
    else:
        winner_id = str(random.choices(CustomerList, weights=((x / Total_Tickets_Bought for x in TicketList)), k=1))[1:-1]     

    end_event(winner_id, event_id)     

#AdminControlPanel
@event.route('/register_event', methods=['POST'])
@requires_access_level(2)
def register_event():
    files = request.files
    params = ('image',)

    form = request.form
    params = ('description', 'product_heading', 'category', 'event_tickets', 'sell_product_price', 'event_prompt')

    if form is None or len(form) != len(params):
        return bad_request_response('Invalid number of arguments')

    for param in params:
        if param not in form:
            return bad_request_response(f'I need a {param} parameter')

    #TODO - Call validators
    image = files['image']
    image.save(os.path.join(config.UPLOAD_FOLDER, secure_filename(image.filename)))
    image = secure_filename(image.filename)
    category = form['category']
    description = form['description']
    product_heading = form['product_heading']
    event_tickets = form['event_tickets']
    total_tickets = form['event_tickets']
    sell_product_price = form['sell_product_price']
    event_prompt = form['event_prompt']
    event_prompt = datetime.strptime(event_prompt, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S.%f+00')

    try:
        event_id = publish_event(image, description, product_heading, category, event_tickets, total_tickets, sell_product_price, event_prompt)
        sched = BackgroundScheduler()
        sched.add_job(endgame, 'date', run_date=datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00'), args=[event_id])
        sched.start()
        return redirect('/' + str(category) + '/' + str(event_id))  #TODO - Pass event_id
    except EventAlreadyExistsException as e:
        return bad_request_response(f'An error occured when publishing the event {e}')

@event.route("/<path:category>/<path:event_id>", methods=['POST', 'GET'])
@requires_access_level(1)
def event_path(event_id, category):
    if "user" in session:
        logged_in = True
        myname, credit = get_user_info(session['user'])
        user_id = get_user_id(session['user'])[0]
        clearance = get_user_from_id(user_id)[1]
        if request.method == 'POST' and "insert_tickets" in request.form:
            return event_subscription(event_id)
        elif request.method == 'POST' and "Product_Qty" in request.form:
            return buy_product(event_id)
    else:
        myname = ''
        credit = 0
        logged_in = False
        clearance = 0

    event_id, image, description, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(int(event_id))
    event_prompt = datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00')
    event_prompt = datetime.now() - event_prompt
    event_prompt = -event_prompt.total_seconds()
    event_prompt = int(event_prompt)
    return render_template("ProductTemplate.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, image=image, description=description, product_heading=product_heading, category=category, event_tickets=event_tickets, progress_perc=progress_perc, sell_product_price=sell_product_price, event_prompt=event_prompt)

def event_subscription(event_id):
    user_id, credit = get_user_id(session['user'])
    credit = int(credit)
    form = request.form
    params = ('insert_tickets',)
     
    if form is None or len(form) != len(params):
        return bad_request_response('Invalid number of arguments')

    for param in params:
        if param not in form:
            return bad_request_response(f'I need a {param} parameter')

    event_id, image, description, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(int(event_id)) #For endpoint to show category
    tickets_bought = int(form['insert_tickets'])
    tickets_left, total_tickets = tickets_amount(event_id)
    credit = credit - tickets_bought
    update_credit(credit, user_id)
    update_perc((((total_tickets - (tickets_left-tickets_bought))/(total_tickets)) * 100), event_id)

    if tickets_bought <= 0:
        return bad_request_response('You need to be more positive')

    if credit >= tickets_bought and tickets_bought <= tickets_left and not if_engaged(user_id, event_id):
        buy_ticket(user_id, event_id, tickets_bought, tickets_left - tickets_bought)
        if tickets_bought == tickets_left:
            CustomerList, TicketList = zip(*[(x[0], x[1]) for x in get_participants(event_id)])
            Total_Tickets_Bought = sum(TicketList)
            winner_id = str(random.choices(CustomerList, weights=((x / Total_Tickets_Bought for x in TicketList)), k=1))[1:-1]
            end_event(winner_id, event_id)
        return redirect('/' + str(category) + '/' + str(event_id))
     
    elif credit >= tickets_bought and tickets_bought <= tickets_left:
        subscribe_again(tickets_bought, user_id, event_id,  tickets_left - tickets_bought)
        if tickets_bought == tickets_left:
            CustomerList, TicketList = zip(*[(x[0], x[1]) for x in get_participants(event_id)])
            Total_Tickets_Bought = sum(TicketList)
            winner_id = str(random.choices(CustomerList, weights=((x / Total_Tickets_Bought for x in TicketList)), k=1))[1:-1]
            end_event(winner_id, event_id)
        return redirect('/' + str(category) + '/' + str(event_id))

    elif not active or credit < tickets_bought or tickets_bought > tickets_left:
        return bad_request_response('You cannot buy this')

def buy_product(event_id):
    user_id, credit = get_user_id(session['user'])
    credit = int(credit)
    form = request.form
    params = ('Product_Qty',)
     
    if form is None or len(form) != len(params):
        return bad_request_response('Invalid number of arguments')

    for param in params:
        if param not in form:
            return bad_request_response(f'I need a {param} parameter')

    event_id, image, description, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(int(event_id)) #For endpoint to show category
    qty_bought = int(form['Product_Qty'])

    if qty_bought < 1:
        return bad_request_response('Dont be a smartass')

    elif credit >= (qty_bought * sell_product_price):
        credit = credit - (qty_bought * sell_product_price)
        update_credit(credit, user_id)
        order_id = new_order(user_id, event_id, qty_bought)
        return redirect('/myOrders')
     
    elif credit < (qty_bought * sell_product_price):
        total_price = (qty_bought * sell_product_price)
        return redirect(url_for('payment.confirm_payment', event_id=event_id, qty_bought=qty_bought, sell_product_price=sell_product_price, image=image, product_heading=product_heading, total_price=total_price, **request.args))

    else:
        return bad_request_response('You cannot buy this')

#AdminControlPanel
@event.route('/edit_event', methods=['POST'])
@requires_access_level(2)
def edit_event():
    form = request.form
    event_id = form['event_id']
    image = request.files['image']
    image.save(os.path.join(config.UPLOAD_FOLDER, secure_filename(image.filename)))
    image = secure_filename(image.filename)
    description = form['description']
    product_heading = form['product_heading']
    category = form['category']
    sell_product_price = form['sell_product_price']
    info_list = [image, description, product_heading, category, sell_product_price]
    conv = lambda i : i or None
    res = [conv(i) for i in info_list]
    image = res[0]
    description = res[1]
    product_heading = res[2]
    category = res[3]
    sell_product_price = res[4]
    update_event(image, description, product_heading, category, sell_product_price, event_id)
    return redirect('/' + str(category) + '/' + str(event_id))

#AdminControlPanel
@event.route('/erase_event', methods=['POST'])
@requires_access_level(2)
def erase_event():
    event_id = request.form['event_id']
    delete_event(event_id)
    return redirect('/TheBrain')

#AdminControlPanel
@event.route('/TheBrain/ManageEvents/List', methods=['GET'])
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
    events = list_events()

    for event_id, product_heading, category, sell_product_price, event_tickets, total_tickets, event_prompt, active, winner_id, created_at in events:
        event_prompt = datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00').strftime('%d %b, %H:%M')
        result.append((event_id, product_heading, category, sell_product_price, event_tickets, total_tickets, event_prompt, active, winner_id, created_at))

    return render_template("EventList.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

#AdminControlPanel
@event.route('/TheBrain/UserSubs', methods=['GET'])
@requires_access_level(2)
def list_subs():
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
    subs = subs_list()

    for user_id, event_id, tickets_bought, last_bought, first_bought in subs:
        result.append((user_id, event_id, tickets_bought, last_bought, first_bought))

    return render_template("UserSubs.html", is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

def bad_request_response(reason):
    '''
        FIXME: Put this in a utils.py
    '''
    response = jsonify({'reason': reason})
    response.status_code = http.HTTPStatus.BAD_REQUEST
    return response
