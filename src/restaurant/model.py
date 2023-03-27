from mesa import Model
from agents.supervisor_agent import SupervisorAgent
from agents.visitor_agent import VisitorAgent
from agents.order_agent import OrderAgent
from agents.operation_agent import OperationAgent
from agents.storage_agent import StorageAgent
from agents.product_agent import ProductAgent
from agents.equipment_agent import EquipmentAgent
from agents.menu_agent import MenuAgent
from agents.cooker_agent import CookerAgent

from sheduler import TimeSheduler
from datetime import time, datetime, timedelta
from agents.message import Message
import json
import os

import logging
logger = logging.getLogger("RestaurantModel")

def load_supervisor_agent(model):
    supervisor = SupervisorAgent(model.next_id(), model)
    model.add_agent(supervisor)

def load_menu_agent(model):
    menu = MenuAgent(model.next_id(), model)
    model.add_agent(menu)

def load_visitors(model):
    current_path = os.path.dirname(os.path.abspath(__file__))
    path_to_visitors = os.path.join(current_path, "../../data/input/visitors.json")
    with open(path_to_visitors, "r") as f:
        data = json.load(f)
        
        for visitor in data['visitors']:
            name = visitor["name"]
            enter_time = visitor["enter_time"]
            current_date = datetime.now()
            enter_time = enter_time.split(":")
            enter_time = time(hour=int(enter_time[0]), minute=int(enter_time[1]))
            enter_time = datetime(current_date.year, current_date.month, current_date.day, enter_time.hour, enter_time.minute)
            agent = VisitorAgent(model.next_id(), model, name=name, enter_time=enter_time)
            model.add_agent(agent)

def load_storage(model):
    storage = StorageAgent(model.next_id(), model)
    model.add_agent(storage)

def load_cookers(model):
    current_path = os.path.dirname(os.path.abspath(__file__))
    path_to_cookers = os.path.join(current_path, "../../data/input/cookers.json")
    with open(path_to_cookers, 'r') as f:
        cookers_data = json.load(f)['cookers']
    for cooker_data in cookers_data:
        if cooker_data['cook_active']:
            name = cooker_data['cook_name']
            cooker = CookerAgent(model.next_id(), model, name)
            cooker.is_busy = False
            model.add_agent(cooker)


class RestaurantModel(Model):
    def __init__(self, start_time = time(hour=8, minute=0), end_time = time(hour=22, minute=0)):
        self.current_id = 0
        self.schedule = TimeSheduler(self, time_step_seconds=1, real_time_speed_up=0, start_time=start_time)
        current_date = datetime.now()
        self.start_time = datetime(current_date.year, current_date.month, current_date.day, start_time.hour, start_time.minute)
        self.end_time = datetime(current_date.year, current_date.month, current_date.day, end_time.hour, end_time.minute)
        self.agents = []
        self.money = 0

        load_supervisor_agent(model=self)
        load_menu_agent(model=self)
        load_storage(model=self)
        load_cookers(model=self)
        load_visitors(model=self)

    def add_agent(self, agent):
        self.agents.append(agent)
        self.schedule.add(agent)

    def remove_agent(self, agent):
        self.agents.remove(agent)
        self.schedule.remove(agent)    

    def send_message(self, message: Message):
        receiver = self.find_agent_by_id(agent_id=message.receiver_id)
        if receiver is not None:
            receiver.receive_message(message)


    def find_agent(self, agent_type):
        for agent in self.agents:
            if isinstance(agent, agent_type) and not agent.is_busy:
                return agent.unique_id
        for agent in self.agents:
            if isinstance(agent, agent_type):
                return agent.unique_id
        return None

    def find_agent_by_id(self, agent_id):
        for agent in self.agents:
            if agent.unique_id == agent_id:
                return agent
        return None

    def step(self):
        self.schedule.step()

    def run_model(self):
        logger.info(f'Ресторан открывается {self.start_time}')
        while self.schedule.time < self.end_time:
            self.step()
        logger.info(f'За день заработано {self.money} рублей')
        logger.info(f'Ресторан закрывается {self.schedule.time}')