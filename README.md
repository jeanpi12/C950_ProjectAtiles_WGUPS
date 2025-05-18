# WGUPS Package Delivery Routing Program

This project simulates and optimizes package deliveries for the Western Governors University Parcel Service (WGUPS). The system routes delivery trucks to ensure that **all 40 packages are delivered on time**, obeying all package constraints while keeping the **total distance traveled under 140 miles**.

## Project Overview

- Implements a **custom-built hash table** for package storage and fast lookup without using any external libraries or built-in dictionaries.
- Optimizes routes using a **greedy algorithm with self-adjusting heuristics** to improve efficiency.
- Simulates truck travel based on real-world constraints such as:
  - Limited truck capacity (16 packages max)
  - Special delivery deadlines
  - Correcting address errors during runtime
- Enables real-time queries to check **package status and delivery times**.
- Tracks and reports the **total mileage** traveled by all trucks.

---

## Core Features

- **Custom Hash Table**  
  Stores package data including ID, address, deadline, city, ZIP code, weight, and status (`At Hub`, `En Route`, `Delivered`).

- **Routing Algorithm**  
  Uses a greedy approach to assign packages to trucks and determine the optimal delivery order with constraints such as delivery deadlines and address correction at 10:20 a.m.

- **Interactive CLI Interface**  
  Allows users to:
  - Query the status of any package at a given time
  - View all package statuses at a given timestamp
  - Display total mileage traveled

- **Simulation Snapshots**  
  Program generates delivery status outputs at the following time intervals:
  - Between 8:35 a.m. and 9:25 a.m.
  - Between 9:35 a.m. and 10:25 a.m.
  - Between 12:03 p.m. and 1:12 p.m.

---

## File Structure

