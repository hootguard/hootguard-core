# Script Name: display_lock.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script provides a thread-safe locking mechanism for the LCD display using Python's `threading.Lock`.
# - Creates a global `display_lock` object to synchronize access to the display.
# - Ensures that multiple threads or processes do not interfere with each other's operations on the display.
# Used in conjunction with other display-related scripts in the HootGuard system.

import threading

display_lock = threading.Lock()
