# driver.py
"""
Driver
Defines the Driver class. Each Driver has an ID and is assigned a Truck.
"""

class Driver:
    def __init__(self, driver_id):
        self.driver_id = driver_id
        self.truck = None

    def assign_truck(self, truck_list):
        for truck in truck_list:
            if truck.driver is None:
                truck.driver = self
                self.truck = truck
                return True
        return False

    def remove_truck(self):
        if self.truck:
            self.truck.driver = None
            self.truck = None
