from enum import Enum
from datetime import time, datetime, timedelta
from .base_agent import BaseAgent
from .supervisor_agent import SupervisorAgent
from .message import Message, MessageType
import random
import pickle

import logging
logger = logging.getLogger("RestaurantModel")

class VisitorState(Enum):
    WAITING = 1
    SEATED = 2
    ORDERED = 3
    WAITING_FOR_ORDER = 4
    EATING = 5
    LEFT = 6

class VisitorAgent(BaseAgent):
    def __init__(self, unique_id: int, model, name: str = None, enter_time: datetime = None):
        super().__init__(unique_id, model)
        self.state = VisitorState.WAITING
        self.name = name
        self.enter_time = enter_time
        self.menu = None
        self.order = None

        if name is None:
            self.name = "Посетитель № " + str(unique_id)

    def enter(self):
        self.state = VisitorState.SEATED
        logger.info(f'{self.name} входит в ресторан {self.model.schedule.time}')
        
    def wait(self):
        pass

    def request_menu(self):
        supervisor_id = self.model.find_agent(SupervisorAgent)
        self.send_message(Message(self.unique_id, supervisor_id, MessageType.MENU_REQUEST))

    def make_order(self):
        if self.menu is None:
            self.request_menu()
        else:
            amount = random.randint(1, 3)
            dishes_to_order = []
            for i in range(amount):
                dishes_to_order.append(random.choice(self.menu))
            supervisor_id = self.model.find_agent(SupervisorAgent)
            message = Message(self.unique_id, supervisor_id, MessageType.ORDER_REQUEST, pickle.dumps((self.unique_id, dishes_to_order)))
            self.send_message(message=message)
            logger.info(f'{self.name} заказывает {", ".join(dishes_to_order)} {self.model.schedule.time}')
            self.state = VisitorState.ORDERED

    def step(self):
        super().step()
        for msg in self.inbox:
            if msg.message_type == MessageType.MENU_RESPOND:
                self.menu = pickle.loads(msg.data)
            if msg.message_type == MessageType.ORDER_CANCEL:
                logger.info(f'Заказ для {self.name} отменен {self.model.schedule.time}')
                logger.info(f'{self.name} выбирает новые блюда {self.model.schedule.time}')
                self.state = VisitorState.SEATED
            if msg.message_type == MessageType.ORDER_CONFIRM:
                self.order = pickle.loads(msg.data)
                wait_time = self.order.get_wait_time()
                logger.info(f'Примерное время ожидания заказа для {self.name} - {wait_time * 60} минут')
                self.state = VisitorState.WAITING_FOR_ORDER
            if msg.message_type == MessageType.ORDER_COMPLETE:
                self.state = VisitorState.EATING
                logger.info(f'Готов заказ для {self.name} {self.model.schedule.time}')
                logger.info(f'{self.name} оплачивает счёт {self.order.get_total_price()} рублей {self.model.schedule.time}')
                self.model.money += self.order.get_total_price()
                self.model.remove_agent(self)
            if msg.message_type == MessageType.ORDER_DELAY:
                logger.info(f'Заказ для {self.name} задерживается в связи с занятостью повара или оборудования {self.model.schedule.time}')
        self.inbox = []

        if self.state == VisitorState.WAITING:
            if self.enter_time is None or self.model.schedule.time >= self.enter_time:
                self.enter()
            else:
                self.wait()
        elif self.state == VisitorState.SEATED:
            self.make_order()
        elif self.state == VisitorState.ORDERED:
            pass
        elif self.state == VisitorState.WAITING_FOR_ORDER:
            pass