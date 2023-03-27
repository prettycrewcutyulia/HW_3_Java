from mesa.time import BaseScheduler
from mesa import Model, Agent
from datetime import time
import datetime
import logging
from model import RestaurantModel

import json
import os

current_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_path, "../../logs/")
log_file = "Model-"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_file = os.path.join(log_path, log_file)
logger = logging.getLogger("RestaurantModel")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(log_file)
logger.addHandler(fh)

def check_input_files():
    directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/input/")
    for file_name in os.listdir(directory):
        if file_name.endswith(".json"):
            file_path = os.path.join(directory, file_name)
            try:
                with open(file_path, "r") as f:
                    json.load(f)
            except ValueError:
                logger.error(" JSON-файл: {}".format(file_path))
                return False
    return True

if __name__ == "__main__":
    if not check_input_files():
        exit(1)
    model = RestaurantModel()
    model.run_model()
