# user_interface.py
"""
User Interface
Provides a helper function to convert a timedelta (from 8:00 AM) into a formatted time string.
"""

from datetime import datetime

def convert_delta_to_time_str(delta):
    base = datetime(2020, 1, 1, 8, 0)
    return (base + delta).strftime("%I:%M %p")
