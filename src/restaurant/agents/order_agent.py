
from .base_agent import BaseAgent
from .storage_agent import StorageAgent
from .menu_agent import MenuAgent
from .operation_agent import OperationAgent
import json
import os
from .message import Message, MessageType

import logging
logger = logging.getLogger("RestaurantModel")

class OrderAgent(BaseAgent):
    def __init__(self, unique_id, model, dishes, visitor_id):
        super().__init__(unique_id, model)
        self.dishes = dishes
        self.visitor_id = visitor_id
        self.needed_products_amount = None
        self.operations = None
        self.delayed_once = False

    def get_products_amount(self):
        menu_agent_id = self.model.find_agent(MenuAgent)
        menu_agent = self.model.find_agent_by_id(menu_agent_id)
        self.needed_products_amount = {}
        for dish in self.dishes:
            dish_card = menu_agent.dish_cards[dish]
            for operation in dish_card["operations"]:
                for product in operation["oper_products"]:
                    self.needed_products_amount[product["prod_type"]] = self.needed_products_amount.get(product["prod_type"], 0) + product["prod_quantity"]

    def check_order_availability(self):
        if self.needed_products_amount == None:
            self.get_products_amount()
        storage_agent_id = self.model.find_agent(StorageAgent)
        storage_agent = self.model.find_agent_by_id(storage_agent_id)
        for product, amount in self.needed_products_amount.items():
            if not storage_agent.check_product_availability(product, amount):
                return False
        return True

    
            
    def reserve_products(self):
        if self.needed_products_amount == None:
            self.get_products_amount()
        storage_agent_id = self.model.find_agent(StorageAgent)
        storage_agent = self.model.find_agent_by_id(storage_agent_id)
        for product, amount in self.needed_products_amount.items():
            storage_agent.reserve_product(product, amount, self.unique_id)

    def cancel(self):
        storage_agent_id = self.model.find_agent(StorageAgent)
        storage_agent = self.model.find_agent_by_id(storage_agent_id)
        storage_agent.release_products(self.unique_id)

    def create_operations(self):
        menu_agent_id = self.model.find_agent(MenuAgent)
        menu_agent = self.model.find_agent_by_id(menu_agent_id)
        self.operations = []
        with open(os.path.join(os.path.dirname(__file__), '../../../data/input/operations.json'), 'r') as f:
            operation_types = json.load(f)['operation_types']
        for dish in self.dishes:
            dish_card = menu_agent.dish_cards[dish]
            for operation in dish_card["operations"]:
                oper_type_id = operation['oper_type']
                oper_type_name = next((ot['oper_type_name'] for ot in operation_types if ot['oper_type_id'] == oper_type_id), None)
                time_float = float(operation['oper_time'])
                op_agent = OperationAgent(unique_id=self.model.next_id(), model=self.model, op_time=time_float, name=oper_type_name, type=oper_type_id, equip_type=operation['equip_type'], order_id=self.unique_id)
                self.model.add_agent(op_agent)
                self.operations.append(op_agent)

    def get_wait_time(self):
        return max([operation.op_time for operation in self.operations])

    def get_total_price(self):
        menu_agent_id = self.model.find_agent(MenuAgent)
        menu_agent = self.model.find_agent_by_id(menu_agent_id)
        return sum([menu_agent.menu_prices[dish] for dish in self.dishes])

    def step(self):
        super().step()
        for msg in self.inbox:
            if msg.message_type == MessageType.OPERATION_DONE:
                for operation in self.operations:
                    if operation.unique_id == msg.sender_id:
                        self.operations.remove(operation)
                        break
                if len(self.operations) == 0:
                    storage_agent_id = self.model.find_agent(StorageAgent)
                    storage_agent = self.model.find_agent_by_id(storage_agent_id)
                    storage_agent.use_products(self.unique_id)
                    self.send_message(Message(self.unique_id, self.visitor_id, MessageType.ORDER_COMPLETE))
                    self.model.remove_agent(self)
                    del self
                    return
            if msg.message_type == MessageType.OPERATION_DELAY:
                if not self.delayed_once:
                    self.delayed_once = True
                    self.send_message(Message(self.unique_id, self.visitor_id, MessageType.ORDER_DELAY))
        self.inbox = []

    