from mesa.time import BaseScheduler
import datetime
from datetime import time, datetime, timedelta
from time import sleep

import logging
logger = logging.getLogger("RestaurantModel")

class TimeSheduler(BaseScheduler):
    def __init__(self, model, start_time = time(hour=8, minute=0), time_step_seconds = 1, real_time_speed_up = 0):
        super().__init__(model)
        current_date = datetime.now()
        self.start_date = datetime(current_date.year, current_date.month, current_date.day, start_time.hour, start_time.minute)
        self.time = self.start_date
        self.time_step_seconds = time_step_seconds
        self.real_time_speed_up = real_time_speed_up
        
    def add(self, agent):
        super().add(agent)
        agent.time = self.time
        
    def step(self):
        for agent in self.agent_buffer(shuffled=False):
            agent.step()
        self.steps += 1
        self.time = datetime.combine(self.time.date(), self.time.time()) + timedelta(seconds=self.time_step_seconds)
        if self.real_time_speed_up > 0:
            sleep(self.time_step_seconds / self.real_time_speed_up)

        
