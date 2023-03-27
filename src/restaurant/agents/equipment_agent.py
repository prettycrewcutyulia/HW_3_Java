from .base_agent import BaseAgent

import logging
logger = logging.getLogger("RestaurantModel")

class EquipmentAgent(BaseAgent):
    def __init__(self, unique_id, model, type, type_id, name):
        super().__init__(unique_id, model)
        self.type = type
        self.type_id = type_id
        self.name = name
        self.is_busy = False

    def step(self):
        super().step()