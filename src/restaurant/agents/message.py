from enum import Enum

import logging
logger = logging.getLogger("RestaurantModel")

class MessageType(Enum):
    PAUSE = -1
    RESUME = 0
    PING = 1
    MENU_REQUEST = 2
    MENU_RESPOND = 3
    ORDER_REQUEST = 4
    ORDER_RESPOND = 5
    ORDER_CONFIRM = 6
    ORDER_CANCEL = 7
    ORDER_COMPLETE = 8
    PROCESS_REQUEST = 9
    PROCESS_RESPOND = 10
    WORK_REQUEST = 11
    WORK_RESPOND = 12
    DISH_REQUEST = 13
    INTSTRUMENTS_REQUEST = 14
    INTSTRUMENTS_RESPOND = 15
    PRODUCT_REQUEST = 16
    PRODUCT_RESPOND = 17
    OPERATION_DONE = 18
    OPERATION_DELAY = 19
    ORDER_DELAY = 20

class Message:
    def __init__(self, sender_id: int, receiver_id: int, message_type: MessageType, data = None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type
        self.data = data
