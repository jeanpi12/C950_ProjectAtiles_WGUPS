# truck.py
"""
Truck

Defines the Truck class used to simulate the delivery trucks.
Each truck has:
  - A unique truck ID.
  - A departure time (as a timedelta from 8:00 AM).
  - A maximum capacity of 16 packages.
  - A current location and mileage tracker.
  - A driver (assigned from driver.py).
  - Methods for loading packages, delivering packages, and returning to the hub.
"""

from datetime import timedelta

class Truck:
    def __init__(self, truck_id, departure_time, speed=18):
        self.truck_id = truck_id
        self.departure_time = departure_time  # For example, timedelta(minutes=0) for 8:00 AM
        self.speed_mph = speed
        self.packages = []  # List of Package objects loaded onto the truck
        self.mileage = 0.0  # Total miles traveled
        self.current_time = departure_time  # Updated as deliveries occur
        self.current_location = "Hub"  # Starting location
        self.hub_address = "Hub"  # For distance lookups, "Hub" is replaced by the first address in distances.csv
        self.delivery_log = []  # Records snapshots for reporting
        self.driver = None  # To be assigned via driver.py

    def is_full(self):
        """Returns True if the truck has reached its maximum capacity (16 packages)."""
        return len(self.packages) >= 16

    def load_package(self, package):
        """
        Loads a package onto the truck if capacity allows.
        Marks the package as assigned to this truck.
        """
        if not self.is_full():
            self.packages.append(package)
            package.assigned_truck_id = self.truck_id
        else:
            raise Exception(f"Truck {self.truck_id} is full.")

    def deliver_package(self, pkg, distance):
        """
        Simulates delivering a package.
          - Updates truck mileage and current time based on the distance traveled.
          - Marks the package as delivered and records the delivery time.
          - Logs the event for reporting.
        Note: The package is already removed from the truck’s packages list in the simulation loop.
        """
        self.mileage += distance
        travel_minutes = (distance / self.speed_mph) * 60.0
        self.current_time += timedelta(minutes=travel_minutes)
        self.current_location = pkg.address
        pkg.status = "Delivered"
        pkg.delivery_time = self.current_time
        self.record_event()

    def send_back_to_hub(self, distance):
        """
        Simulates the truck returning to the hub:
          - Updates mileage and current time.
          - Sets the current location to "Hub".
          - Logs the event.
        """
        self.mileage += distance
        travel_minutes = (distance / self.speed_mph) * 60.0
        self.current_time += timedelta(minutes=travel_minutes)
        self.current_location = "Hub"
        self.record_event()

    def record_event(self):
        """
        Records a snapshot of the truck's state for reporting:
          - Current time, location, mileage, and the list of remaining package IDs.
        """
        snapshot = {
            "time": self.current_time,
            "location": self.current_location,
            "mileage": self.mileage,
            "undelivered": [p.package_id for p in self.packages],
        }
        self.delivery_log.append(snapshot)
