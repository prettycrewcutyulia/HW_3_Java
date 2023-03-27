from .base_agent import BaseAgent
from datetime import datetime
from .storage_agent import StorageAgent
from .cooker_agent import CookerAgent
from .message import Message, MessageType
import os

import logging
logger = logging.getLogger("RestaurantModel")

class OperationAgent(BaseAgent):
    def __init__(self, unique_id, model, op_time, name, type, equip_type, order_id):
        super().__init__(unique_id, model)
        self.order_id = order_id
        self.start_time = None
        self.type = type
        self.name = name
        self.equip_type = equip_type
        self.op_time = op_time
        self.state = "waiting"

    def reserve_equipment(self):
        storage_agent_id = self.model.find_agent(StorageAgent)
        storage_agent = self.model.find_agent_by_id(storage_agent_id)
        storage_agent.reserve_equipment(self.equip_type, self.unique_id)

    def release_equipment(self):
        storage_agent_id = self.model.find_agent(StorageAgent)
        storage_agent = self.model.find_agent_by_id(storage_agent_id)
        storage_agent.release_equipment(self.unique_id)

    def check_equipment_availability(self):
        storage_agent_id = self.model.find_agent(StorageAgent)
        storage_agent = self.model.find_agent_by_id(storage_agent_id)
        return storage_agent.check_equipment_availability(self.equip_type)

    def find_cooker(self):
        cooker_agent_id = self.model.find_agent(CookerAgent)
        if cooker_agent_id == None:
            return None
        cooker_agent = self.model.find_agent_by_id(cooker_agent_id)
        if cooker_agent.is_busy:
            return None
        return cooker_agent

    def step(self):
        super().step()
        if self.state == "waiting":
            cooker = self.find_cooker()
            if cooker == None:
                self.send_message(Message(self.unique_id, self.order_id, MessageType.OPERATION_DELAY))
                return
            if not self.check_equipment_availability():
                self.send_message(Message(self.unique_id, self.order_id, MessageType.OPERATION_DELAY))
                return
            cooker.is_busy = True
            self.cooker = cooker
            self.reserve_equipment()
            self.start_time = self.model.schedule.time
            logger.info(f'Повар {self.cooker.name} начал операцию {self.name} {self.start_time}')
            self.state = "in_progress"
        elif self.state == "in_progress":
            if self.start_time == None:
                return
            time_diff = self.model.schedule.time - self.start_time
            time_diff_hours = time_diff.total_seconds() / 60 / 60
            if time_diff_hours >= float(self.op_time):
                self.release_equipment()
                self.cooker.is_busy = False
                self.state = "done"
        elif self.state == "done":
            self.send_message(Message(self.unique_id, self.order_id, MessageType.OPERATION_DONE, self.name))
            self.state = "finished"
            self.model.remove_agent(self)
            del self
            return
