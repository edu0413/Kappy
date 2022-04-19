from src.adapter.lootbox_repository import database_lootbox
from src.adapter.lootboxinv_repository import database_lootboxinv

def publish_lootbox(lootbox_list):
    return database_lootbox.publish_lootbox(lootbox_list)

def get_loot_ids():
    return database_lootbox.get_loot_ids()

def lootbox_items(lootbox_id, product_id):
    return database_lootbox.lootbox_items(lootbox_id, product_id)

def get_lootbox(user_id, lootbox_id, product_id):
    return database_lootboxinv.get_lootbox(user_id, lootbox_id, product_id)

def get_inv_ids(user_id):
    return database_lootboxinv.get_inv_ids(user_id)

def inventory_items(inventory_id):
    return database_lootboxinv.inventory_items(inventory_id)