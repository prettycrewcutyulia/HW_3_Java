from mesa import Agent
from abc import abstractmethod
from .message import Message, MessageType

import logging
import datetime
import os

current_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_path, "../../../logs/")
log_file = "TechLog-"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_file = os.path.join(log_path, log_file)
logger2 = logging.getLogger("TechLog")
logger2.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_file)
logger2.addHandler(fh)


class BaseAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.inbox = []
        self.is_busy = False
        logger2.info(f'Создан агент класса {self.__class__.__name__} под id {self.unique_id}')

    def step(self):
        logger2.info(f'Агент {self.unique_id} класса {self.__class__.__name__} выполняет шаг')

    def find_agent(self, agent_type):
        return self.model.find_agent(agent_type)

    def send_message(self, message: Message):
        self.model.send_message(message)

    def receive_message(self, message: Message):
        if message.message_type == MessageType.PAUSE:
            self.pause()
        elif message.message_type == MessageType.RESUME:
            self.resume()
        else:
            self.inbox.append(message)

    def pause(self):
        if event.sender == self:
            self.model.schedule.remove(self)
        
    def resume(self):
        if event.sender == self:
            self.model.schedule.add(self)
