from .base_agent import BaseAgent
from .message import Message, MessageType
from .storage_agent import StorageAgent
import os
import pickle
import json

import logging
logger = logging.getLogger("RestaurantModel")

class MenuAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.dish_cards = {}
        self.menu_prices = {}
        self.menu = self.load_menu()
        
    def load_menu(self):
        with open(os.path.join(os.path.dirname(__file__), '../../../data/input/menu.json'), 'r') as f:
            menu_data = json.load(f)
        
        with open(os.path.join(os.path.dirname(__file__), '../../../data/input/dish_cards.json'), 'r') as f:
            dish_data = json.load(f)

        for menu_dish in menu_data['menu_dishes']:
            if menu_dish["menu_dish_active"]:
                card_id = menu_dish["menu_dish_card"]
                for dish_card in dish_data['dish_cards']:
                    if dish_card["card_id"] == card_id:
                        self.dish_cards[dish_card['dish_name']] = dish_card
        
        self.menu_prices = {}
        for dish in self.dish_cards:
            price = 0
            for menu_dish in menu_data['menu_dishes']:
                if menu_dish["menu_dish_active"] and self.dish_cards[dish]["card_id"] == menu_dish["menu_dish_card"]:
                    price = menu_dish["menu_dish_price"]
                    break
            self.menu_prices[dish] = price

        return list(self.dish_cards.keys())

    def update_menu(self):
        self.menu = []
        for dish in self.dish_cards:
            if self.check_dish_availability(dish):
                self.menu.append(dish)

    def check_dish_availability(self, dish):
        storage_agent_id = self.model.find_agent(StorageAgent)
        dish_card = self.dish_cards[dish]
        for operation in dish_card["operations"]:
            if not storage_agent.check_product_availability(operation["product"], operation["amount"]):
                return False
        
    def get_menu(self):
        return self.menu

    def get_visitors_menu(self, visitor_id):
        p = pickle.dumps((visitor_id, self.menu))
        return p
    
    def step(self):
        super().step()
        for msg in self.inbox:
            if msg.message_type == MessageType.MENU_REQUEST:
                self.send_message(Message(self.unique_id, msg.sender_id, MessageType.MENU_RESPOND, self.get_visitors_menu(int(msg.data))))
        self.inbox = []