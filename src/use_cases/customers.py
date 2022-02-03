from src.adapter.customers_repository import database_customers

def if_engaged(user_id, event_id):
    return database_customers.if_engaged(user_id, event_id)

def buy_ticket(user_id, event_id, tickets_bought, tickets_remaining):
    return database_customers.buy_ticket(user_id, event_id, tickets_bought, tickets_remaining)

def subscribe_again(tickets_bought, user_id, event_id, tickets_remaining):
    return database_customers.subscribe_again(tickets_bought, user_id, event_id, tickets_remaining)

def tickets_amount(event_id):
    return database_customers.tickets_amount(event_id)

def get_participants(event_id):
    return database_customers.get_participants(event_id)

def user_events(user_id):
    return database_customers.user_events(user_id)

def subs_list():
    return database_customers.subs_list()