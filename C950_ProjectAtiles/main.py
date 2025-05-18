# main.py
# Jean-Pierre Atiles
# Student ID: 011028774
"""
WGUPS Routing Program

This program loads package data from 'packages.csv' into a custom hash table,
Assigns packages to trucks so that:
  • Packages 13,14,15,16,19,20 are together (Truck 1).
  • Packages 3,18,36,38 plus any packages delayed on flight (packages 6,25,28,32) are assigned to Truck 2.
The remaining packages are distributed among Truck 1, Truck 2, and Truck 3 so that no truck carries more than 16 packages.
Before simulation, each truck’s package list is sorted by deadline
so that packages with earlier deadlines are delivered first. Delayed packages are not delivered before 9:05 AM.
Additionally, package 9’s wrong address is updated to the correct one only at or after 10:20 AM.
"""

import csv, re
from datetime import datetime, timedelta
from driver import Driver
from hash_table import HashTable
from package import Package
from truck import Truck
from user_interface import convert_delta_to_time_str

#  Deadline Conversion

def deadline_to_timedelta(deadline_str):
    """Convert a deadline string (e.g. '10:30 AM' or 'EOD') into a timedelta from 8:00 AM.
       Here 'EOD' is interpreted as 5:00 PM (i.e. 9 hours after 8:00 AM)."""
    if deadline_str.strip().upper() == "EOD":
        return timedelta(hours=9)
    else:
        dt = datetime.strptime(deadline_str, "%I:%M %p")
        base = datetime(2020, 1, 1, 8, 0)
        return datetime(2020, 1, 1, dt.hour, dt.minute) - base

#  Address Matching

def normalize_address(addr):
    norm = " ".join(addr.strip().split()).lower()
    norm = re.sub(r'[^\w\s]', '', norm)
    return norm

def extract_street_info(addr):
    tokens = normalize_address(addr).split()
    return " ".join(tokens[:3])

def find_address_index(address, address_list):
    norm_address = normalize_address(address)
    for i, addr in enumerate(address_list):
        if normalize_address(addr) == norm_address:
            return i
    key = extract_street_info(address)
    for i, addr in enumerate(address_list):
        if extract_street_info(addr) == key:
            return i
    print("Normalized addresses from distances.csv:")
    for a in address_list:
        print(" -", normalize_address(a))
    raise ValueError(f"Address '{address}' not found in address list.")

def load_address_data():
    with open('distances.csv', 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        header = next(reader, None)
        if header:
            return [cell.strip() for cell in header[1:]]
        return []

def distance_between(address1, address2):
    return 3.0

#  Package Loading

def load_packages_into_hash(filename, package_hash):
    with open(filename, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader, None)  # skip header
        for row in reader:
            pkg_id = int(row[0])
            street = row[1].strip()
            city = row[2].strip()
            state = row[3].strip()
            zip_code = row[4].strip()
            address = f"{street}, {city}, {state} {zip_code}"
            deadline = row[5].strip()
            weight = row[6].strip()
            notes = row[7].strip()
            p = Package(pkg_id, address, city, state, zip_code, deadline, weight, notes)
            # Save original address for package 9 for later correction.
            if pkg_id == 9:
                p.original_address = address
            package_hash.insert(pkg_id, p)

#  Truck & Driver Initialization

def initialize_trucks_drivers(num_trucks, num_drivers):
    truck_list = []
    # Truck 2 departs at 9:05 AM; others at 8:00 AM.
    for i in range(1, num_trucks+1):
        if i == 2:
            truck_list.append(Truck(i, departure_time=timedelta(minutes=65)))
        else:
            truck_list.append(Truck(i, departure_time=timedelta(minutes=0)))
    driver_list = []
    for i in range(1, num_drivers+1):
        d = Driver(i)
        d.assign_truck(truck_list)
        driver_list.append(d)
    return truck_list, driver_list

#  Hard-Coded Truck Loads
#  assignments:
#    group 1: {13,14,15,16,19,20} must be together.
#    group 2: {3,18,36,38} plus all delayed packages (those with "delayed on flight") must go to Truck 2.
def hard_code_truck_loads(package_hash, truck_list):
    # Clear any preexisting loads.
    for t in truck_list:
        t.packages.clear()
    all_ids = set(range(1, 41))
    forced_truck1 = {13, 14, 15, 16, 19, 20}
    forced_truck2 = {3, 18, 36, 38}
    # Also, add delayed packages (if not already forced) to Truck 2.
    for pid in all_ids - forced_truck1 - forced_truck2:
        pkg = package_hash.lookup(pid)
        if "delayed on flight" in pkg.special_note.lower():
            forced_truck2.add(pid)
    # Remaining packages are those not forced.
    remaining = sorted(list(all_ids - forced_truck1 - forced_truck2))
    # We want total loads:
    # Truck 1:  group1 (6 packages) plus 10 more = 16 total.
    # Truck 2:  group2 now (say 8 packages) plus 8 more = 16 total.
    # Truck 3 gets the remaining (40 - 16 - 16 = 8 packages).
    # Assign first 10 from remaining to Truck 1, next 8 to Truck 2, and last 8 to Truck 3.
    rem_for_truck1 = set(remaining[:10])
    rem_for_truck2 = set(remaining[10:18])
    rem_for_truck3 = set(remaining[18:])
    load_truck1 = sorted(list(forced_truck1.union(rem_for_truck1)))
    load_truck2 = sorted(list(forced_truck2.union(rem_for_truck2)))
    load_truck3 = sorted(list(rem_for_truck3))
    # Load packages to each truck (ensuring capacity is not exceeded).
    for pid in load_truck1:
        pkg = package_hash.lookup(pid)
        try:
            truck_list[0].load_package(pkg)
        except Exception as e:
            print(e)
    for pid in load_truck2:
        pkg = package_hash.lookup(pid)
        try:
            truck_list[1].load_package(pkg)
        except Exception as e:
            print(e)
    for pid in load_truck3:
        pkg = package_hash.lookup(pid)
        try:
            truck_list[2].load_package(pkg)
        except Exception as e:
            print(e)

#  Delivery Simulation
# Before delivering, sort each truck’s package list by deadline (earlier deadlines first).
def run_deliveries_for_truck(truck):
    # Sort packages by deadline (using deadline_to_timedelta).
    truck.packages.sort(key=lambda pkg: deadline_to_timedelta(pkg.deadline))
    current_address = "Hub"
    while truck.packages:
        candidate = None
        candidate_index = None
        earliest_deadline = timedelta(hours=100)
        for i, pkg in enumerate(truck.packages):
            d = distance_between(current_address, pkg.address)
            # For flight-delayed packages, skip if truck hasn't reached 9:05 AM.
            if "delayed on flight" in pkg.special_note.lower() and truck.current_time < timedelta(minutes=65):
                continue
            pkg_deadline = deadline_to_timedelta(pkg.deadline)
            if truck.current_time + timedelta(minutes=(d / truck.speed_mph) * 60) <= pkg_deadline:
                if pkg_deadline < earliest_deadline:
                    earliest_deadline = pkg_deadline
                    candidate = pkg
                    candidate_index = i
        if candidate is None:
            print(f"ERROR: Truck {truck.truck_id} cannot deliver remaining packages on time.")
            break
        pkg = truck.packages.pop(candidate_index)
        d = distance_between(current_address, pkg.address)
        truck.deliver_package(pkg, d)
        pkg.truck_id = truck.truck_id  # record which truck delivered this package
        # For package 9, update the address at or after 10:20 AM.
        if pkg.package_id == 9 and truck.current_time >= timedelta(hours=2, minutes=20):
            pkg.address = "Third District Juvenile Court 410 S State St, Salt Lake City, UT 84111"
        current_address = pkg.address
    d_back = distance_between(current_address, "Hub")
    truck.send_back_to_hub(d_back)

def simulate_deliveries(package_hash, truck_list):
    for truck in truck_list:
        run_deliveries_for_truck(truck)
    # Check deadlines for each package.
    for pid in range(1, 41):
        pkg = package_hash.lookup(pid)
        if pkg.delivery_time and pkg.delivery_time > deadline_to_timedelta(pkg.deadline):
            print(f"WARNING: Package {pid} was delivered after its deadline!")

#  Interactive Menu
def prompt_interactive_menu(package_hash, truck_list):
    while True:
        print("\n-------------------------------------------")
        print("Western Governors University Parcel Service")
        print("-------------------------------------------")
        print("Please select a menu option:")
        print("\t1. General Report")
        print("\t2. Package Query")
        print("\t3. Exit")
        choice = input("Enter your option selection here: ").strip()
        if choice == "1":
            delta = prompt_time()
            show_general_report(package_hash, truck_list, delta)
        elif choice == "2":
            delta = prompt_time()
            pid = prompt_package_id(package_hash)
            show_package_status(package_hash, pid, truck_list, delta)
        elif choice == "3":
            print("Exiting program.")
            exit()
        else:
            print("Invalid selection.")

def prompt_time():
    while True:
        t = input("Please provide a time for the report in the format [HOUR:MINUTE AM/PM]: ")
        try:
            dt_parsed = datetime.strptime(t, "%I:%M %p")
            base = datetime(2020, 1, 1, 8, 0)
            dt = datetime(2020, 1, 1, dt_parsed.hour, dt_parsed.minute)
            delta = dt - base
            return delta if delta > timedelta(0) else timedelta(0)
        except Exception as e:
            print("Error: Invalid time format. Please try again.", e)

def prompt_package_id(package_hash):
    while True:
        pid = input("Please enter the ID of the package you would like to view: ")
        if pid.isdigit():
            pid = int(pid)
            if package_hash.lookup(pid) is not None:
                return pid
            else:
                print("Package not found.")
        else:
            print("Invalid package ID.")

def show_general_report(package_hash, truck_list, report_delta):
    print("\nStatus report of all packages at " + convert_delta_to_time_str(report_delta))
    print("---------------------------------------------------------------------")
    for pid in range(1, 41):
        pkg = package_hash.lookup(pid)
        if pkg.delivery_time and pkg.delivery_time <= report_delta:
            status = "Delivered"
            dt_str = convert_delta_to_time_str(pkg.delivery_time)
        else:
            status = "In Transit"
            dt_str = "N/A"
        # For package 9, display corrected address only if report time >= 10:20 AM.
        if pkg.package_id == 9:
            display_address = ( "Third District Juvenile Court 410 S State St, Salt Lake City, UT 84111"
                                if report_delta >= timedelta(hours=2, minutes=20)
                                else pkg.original_address )
        else:
            display_address = pkg.address
        print(f"Package {pkg.package_id}: {display_address} | Deadline: {pkg.deadline} | Weight: {pkg.weight} kg | "
              f"Special Notes: {pkg.special_note if pkg.special_note else 'None'} | Status: {status} | "
              f"Delivery Time: {dt_str} | Truck: {pkg.truck_id if pkg.truck_id else 'N/A'}")
    total = 0.0
    for truck in truck_list:
        mileage = 0.0
        for snap in truck.delivery_log:
            if snap["time"] <= report_delta:
                mileage = snap["mileage"]
            else:
                break
        print(f"Truck {truck.truck_id} mileage at {convert_delta_to_time_str(report_delta)}: {mileage:.2f} miles")
        total += mileage
    print(f"Total mileage at {convert_delta_to_time_str(report_delta)}: {total:.2f} miles\n")

def show_package_status(package_hash, pkg_id, truck_list, report_delta):
    pkg = package_hash.lookup(pkg_id)
    if pkg.delivery_time and pkg.delivery_time <= report_delta:
        status = "Delivered"
        dt_str = convert_delta_to_time_str(pkg.delivery_time)
    else:
        status = "In Transit"
        dt_str = "N/A"
    if pkg.package_id == 9:
        display_address = ( "Third District Juvenile Court 410 S State St, Salt Lake City, UT 84111"
                            if report_delta >= timedelta(hours=2, minutes=20)
                            else pkg.original_address )
    else:
        display_address = pkg.address
    print(f"\nPackage {pkg_id}:")
    print(f"  Address: {display_address}")
    print(f"  Deadline: {pkg.deadline}")
    print(f"  Weight: {pkg.weight} kg")
    print(f"  Special Notes: {pkg.special_note if pkg.special_note else 'None'}")
    print(f"  Status: {status}")
    print(f"  Delivery Time: {dt_str}")
    print(f"  Delivered by Truck: {pkg.truck_id if pkg.truck_id else 'N/A'}\n")

#  Main

def main():
    package_hash = HashTable()
    load_packages_into_hash("packages.csv", package_hash)
    truck_list, driver_list = initialize_trucks_drivers(3, 2)
    hard_code_truck_loads(package_hash, truck_list)
    simulate_deliveries(package_hash, truck_list)
    prompt_interactive_menu(package_hash, truck_list)

if __name__ == "__main__":
    main()
