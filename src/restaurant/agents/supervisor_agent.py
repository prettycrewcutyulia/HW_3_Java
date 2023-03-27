from .base_agent import BaseAgent
from .message import Message, MessageType
from .menu_agent import MenuAgent
from .order_agent import OrderAgent
import pickle

import logging
logger = logging.getLogger("RestaurantModel")

class SupervisorAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        super().step()
        for msg in self.inbox:
            if msg.message_type == MessageType.MENU_REQUEST:
                menuAgent_id = self.model.find_agent(MenuAgent)
                self.send_message(Message(self.unique_id, menuAgent_id, MessageType.MENU_REQUEST, str(msg.sender_id)))
            if msg.message_type == MessageType.MENU_RESPOND:
                visitor_id, menu = pickle.loads(msg.data)
                menu = pickle.dumps(menu)
                self.send_message(Message(self.unique_id, int(visitor_id), MessageType.MENU_RESPOND, menu))
            if msg.message_type == MessageType.ORDER_REQUEST:
                visitor_id, dishes = pickle.loads(msg.data)
                order = OrderAgent(self.model.next_id(), self.model, dishes, visitor_id)
                if order.check_order_availability():
                    self.model.add_agent(order)
                    order.reserve_products()
                    order.create_operations()
                    order_str = pickle.dumps(order)
                    self.send_message(Message(self.unique_id, int(visitor_id), MessageType.ORDER_CONFIRM, order_str))
                else:
                    self.send_message(Message(self.unique_id, int(visitor_id), MessageType.ORDER_CANCEL, ''))
        self.inbox = []
