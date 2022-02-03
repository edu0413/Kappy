"""
Code related to the event listing
"""

import os, http, time
from flask import Blueprint, render_template, jsonify, request, session
from src.use_cases.events import get_all_ids, get_category_ids, get_all_params
from src.use_cases.customers import user_events
from src.use_cases.orders import user_orders
from src.use_cases.register import get_user_info, get_user_id
from src.web.auth import requires_access_level
from src.use_cases.register import get_user_id
from src.use_cases.user import get_user_from_id
from datetime import datetime

events_list = Blueprint('events_list', __name__, template_folder='templates')

@events_list.route('/')
def index():
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

    event_ids = [x[0] for x in get_all_ids(True)][-6:]
    result = []

    for event_id in event_ids:
        event_id, image, description, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(event_id)
        event_prompt = datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00').strftime('%d %b, %H:%M')
        result.append((event_id, image, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))

    event_ids = get_all_ids(True)
    Allresult = []

    for event_id in event_ids:
        event_id, image, description, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(event_id)
        event_prompt = datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00').strftime('%d %b, %H:%M')
        Allresult.append((event_id, image, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))

    IMresult, JOresult, TCresult, VUresult, VGresult = [], [], [], [], []
    categories = ["Imóveis", "Joalheria", "Tecnologia", "Veículos", "Viagens"]
    for category in categories:
        event_ids = get_category_ids(category, True)
        for event_id in event_ids:
            event_id, image, description, product_heading, category, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(event_id)
            event_prompt = datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00').strftime('%d-%m-%Y às %H:%M')
            if category == "Imóveis":
                IMresult.append((event_id, image, product_heading, "Imóveis", event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))
            elif category == "Joalheria":
                JOresult.append((event_id, image, product_heading, "Joalheria", event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))
            elif category == "Tecnologia":
                TCresult.append((event_id, image, product_heading, "Tecnologia", event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))
            elif category == "Veículos":
                VUresult.append((event_id, image, product_heading, "Veículos", event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))
            elif category == "Viagens":
                VGresult.append((event_id, image, product_heading, "Viagens", event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))

    return render_template('index.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result, Allresult=Allresult, IMresult=IMresult, JOresult=JOresult, TCresult=TCresult, VUresult=VUresult, VGresult=VGresult)

@events_list.route('/oldEvents')
@requires_access_level(2)
def get_oldevents():
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
    active = False
    categories = ["Imóveis", "Joalheria", "Tecnologia", "Veículos", "Viagens"]
    for category in categories:
        lists_category = []
        event_ids = get_category_ids(category, active)
        for event_id in event_ids:
            event_id, image, description, product_heading, category_event, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id, created_at = get_all_params(event_id)
            event_prompt = datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00').strftime('%d-%m-%Y às %H:%M')
            lists_category.append((event_id, image, product_heading, category_event, event_tickets, total_tickets, progress_perc, sell_product_price, event_prompt, active, winner_id))

        result.append((category, lists_category))
                    
    return render_template('OldEventsPage.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

@events_list.route('/myEvents')
@requires_access_level(1)
def list_event():
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

    user_id = get_user_id(session['user'])[0]
    result, oldresult = [], []
    events = user_events(user_id)
     
    for user_id, event_id, image, tickets_bought, product_heading, category, event_tickets, sell_product_price, event_prompt, progress_perc, active in events:
        event_prompt = datetime.strptime(event_prompt, '%Y-%m-%d %H:%M:%S.%f+00').strftime('%d %b, %H:%M')
        if active == True:
            result.append((user_id, event_id, image, tickets_bought, product_heading, category, event_tickets, sell_product_price, event_prompt, progress_perc, active)) #FIXME: Raise an exception if customer is not participating in events
        elif active == False:
            oldresult.append((user_id, event_id, image, tickets_bought, product_heading, category, event_tickets, sell_product_price, event_prompt, progress_perc, active)) #FIXME: Raise an exception if customer is not participating in events

    return render_template('myEvents.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result, oldresult=oldresult)

@events_list.route('/myOrders')
@requires_access_level(1)
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

    user_id = get_user_id(session['user'])[0]
    result = []
    events = user_orders(user_id)
     
    for order_id, user_id, event_id, qty_bought, status, image, product_heading, category, created_at in events:
        created_at = created_at.strftime('%d %b de %Y, %H:%M')
        result.append((order_id, user_id, event_id, qty_bought, status, image, product_heading, category, created_at)) #FIXME: Raise an exception if customer is not participating in events

    return render_template('myOrders.html', is_logged_in=logged_in, clearance_level=clearance, myName=myname, credit=credit, result=result)

def bad_request_response(reason):
    response = jsonify({'reason': reason})
    response.status_code = http.HTTPStatus.BAD_REQUEST
    return response