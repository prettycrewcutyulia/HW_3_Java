from .base_agent import BaseAgent

import logging
logger = logging.getLogger("RestaurantModel")

class CookerAgent(BaseAgent):
    def __init__(self, unique_id, model, name):
        super().__init__(unique_id, model)
        self.name = name
        self.is_busy = False
    
    def step(self):
        super().step()