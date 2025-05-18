# package.py
"""
Package
Defines the Package class to store package details.
"""

class Package:
    def __init__(self, package_id, full_address, city, state, zip_code, deadline, weight, special_note=""):
        self.package_id = package_id
        self.address = full_address  # For output
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.special_note = special_note
        self.status = "At Hub"  # Options: "At Hub", "En Route", "Delivered"
        self.delivery_time = None
        self.truck_id = None  # Truck that delivered the package
        self.assigned_truck = None
        self.original_address = None  # To store the wrong address for package #9

    def is_truck_assigned(self):
        return self.assigned_truck is not None

    def __str__(self):
        dt_str = str(self.delivery_time) if self.delivery_time else "N/A"
        return (f"Package {self.package_id}: {self.address} | Deadline: {self.deadline} | "
                f"Weight: {self.weight} | Status: {self.status} | Delivery Time: {dt_str}")
