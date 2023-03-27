from .base_agent import BaseAgent
from .equipment_agent import EquipmentAgent
from .product_agent import ProductAgent
import json
import os
import datetime

import logging
logger = logging.getLogger("RestaurantModel")

class StorageAgent(BaseAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.equipment_agents = []
        self.product_agents = []

        self.load_equipment()
        self.load_products()
    
    def load_equipment(self):
        with open(os.path.join(os.path.dirname(__file__), '../../../data/input/equipment_type.json'), 'r') as f:
            equip_types = json.load(f)['equipment_type']
        
        with open(os.path.join(os.path.dirname(__file__), '../../../data/input/equipment.json'), 'r') as f:
            equipment = json.load(f)['equipment']
            
        equip_type_dict = {equip_type['equip_type_id']: equip_type['equip_type_name'] for equip_type in equip_types}

        for equip in equipment:
            equip_type = equip['equip_type']
            equip_name = equip['equip_name']
            is_active = equip['equip_active']

            if is_active:
                new_equip_agent = EquipmentAgent(unique_id=self.model.next_id(), model=self.model,
                                                type=equip_type_dict[equip_type], name=equip_name, type_id=equip_type)
                new_equip_agent.is_busy = False

                self.model.add_agent(new_equip_agent)
                self.equipment_agents.append(new_equip_agent)
    
    def load_products(self):
        with open(os.path.join(os.path.dirname(__file__), '../../../data/input/product_types.json'), 'r') as f:
            product_types = json.load(f)['product_types']
        
        with open(os.path.join(os.path.dirname(__file__), '../../../data/input/products.json'), 'r') as f:
            products = json.load(f)['products']
            
        product_type_dict = {prod_type['prod_type_id']: prod_type for prod_type in product_types}

        for prod in products:
            prod_item_id = prod['prod_item_id']
            prod_item_type = prod['prod_item_type']
            prod_item_name = prod['prod_item_name']
            prod_item_unit = prod['prod_item_unit']
            prod_item_quantity = prod['prod_item_quantity']

            new_prod_agent = ProductAgent(unique_id=self.model.next_id(), model=self.model,
                                          name=prod_item_name, quantity=prod_item_quantity, unit=prod_item_unit, ptype=prod_item_type)
            self.product_agents.append(new_prod_agent)

    def check_product_availability(self, product_type, amount):
        for product in self.product_agents:
            if product.type == product_type and product.quantity >= amount:
                return True
        return False

    def reserve_product(self, product_type, amount, order_id):
        for product in self.product_agents:
            if product.type == product_type and product.quantity >= amount:
                product.reserve(amount, order_id)
                return True
        return False

    def release_products(self, order_id):
        for product in self.product_agents:
            if order_id in product.reserved:
                product.release(order_id)
                return True
        return False

    def use_products(self, order_id):
        for product in self.product_agents:
            if order_id in product.reserved:
                product.use(order_id)
                return True
        return False

    def reserve_equipment(self, type, operation_id):
        for equipment in self.equipment_agents:
            if equipment.type == type and not equipment.is_busy:
                equipment.reserve(operation_id)
                return True
        return False

    def release_equipment(self, operation_id):
        for equipment in self.equipment_agents:
            if equipment.is_busy and equipment.reserved == operation_id:
                equipment.release()
                return True
        return False

    def check_equipment_availability(self, etype):
        for equipment in self.equipment_agents:
            if equipment.type_id == etype and not equipment.is_busy:
                return True
        return False

    def step(self):
        super().step()