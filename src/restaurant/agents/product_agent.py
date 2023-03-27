from .base_agent import BaseAgent

import logging
logger = logging.getLogger("RestaurantModel")

class ProductAgent(BaseAgent):
    def __init__(self, unique_id, model, name, quantity, unit, ptype):
        super().__init__(unique_id, model)
        self.name = name
        self.type = ptype
        self.quantity = quantity
        self.unit = unit
        self.reserved = {}

    def reserve(self, amount, order_id):
        self.reserved[order_id] = amount
        self.quantity -= amount

    def release(self, order_id):
        self.quantity += self.reserved[order_id]
        del self.reserved[order_id]

    def use(self, order_id):
        del self.reserved[order_id]

    def step(self):
        super().step()
