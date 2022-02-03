from src.adapter.events_repository import database_events

def get_all_ids(active):
    return database_events.get_all_ids(active)

def get_category_ids(category, active):
    return database_events.get_category_ids(category, active)

def get_all_params(event_id):
    return database_events.get_all_params(event_id)

def publish_event(image, description, product_heading, category, event_tickets, total_tickets, sell_product_price, event_prompt):
    try:
        return database_events.publish_event(image, description, product_heading, category, event_tickets, total_tickets, sell_product_price, event_prompt)
    except Exception as e:
        print(e)
        raise CouldntPublishEvent(e)

def update_event(image, description, product_heading, category, sell_product_price, event_id):
    return database_events.update_event(image, description, product_heading, category, sell_product_price, event_id)

def delete_event(event_id):
    return database_events.delete_event(event_id)

def list_events():
    return database_events.list_events()

def update_perc(progress_perc, event_id):
    return database_events.update_perc(progress_perc, event_id)

def end_event(winner_id, event_id):
    return database_events.end_event(winner_id, event_id)

class CouldntPublishEvent(Exception):
    def __init__(self, e):
        super(Exception, self).__init__(f"Could not publish event [{e}]")
