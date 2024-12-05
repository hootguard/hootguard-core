# Script Name: info_main.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script manages the display functionality for the HootGuard system, allowing users to view system information 
# (IP address, snooze time, and version) by pressing a button. Key features include:
# - Detects button presses on a GPIO pin and maps each press to a specific display function:
#   - 1st press: Display IP address.
#   - 2nd press: Display snooze time.
#   - 3rd press: Display version, then reset to initial state.
# - Implements a debounce mechanism to avoid accidental multiple detections of a single press.
# - Uses a separate thread to handle the display and deactivate it after 10 seconds of inactivity.
# - Ensures thread-safe access to the display using `display_lock`.
# Runs continuously, listening for button presses, and cleans up GPIO resources on termination.

import RPi.GPIO as GPIO
import subprocess
import threading
import time
from display_lock import display_lock

# Pin Setup
BUTTON_PIN = 7  # GPIO 7 (Pin 26)

GPIO.setmode(GPIO.BCM)  # BCM = GPIO numbering (BOARD = pin numbering)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Global variables
last_press_time = 0
debounce_time = 0.2  # 200 milliseconds
press_count = 0  # Count of button presses
display_thread = None
stop_event = threading.Event()

def display_ip_address():
    subprocess.run(["/usr/bin/python3", "/opt/hootguard/display/info_show_ip.py"])

def display_snooze_time():
    subprocess.run(["/usr/bin/python3", "/opt/hootguard/display/info_show_snooze.py"])

def display_version():
    subprocess.run(["/usr/bin/python3", "/opt/hootguard/display/info_show_version.py"])

def deactivate_display():
    subprocess.run(["/usr/bin/python3", "/opt/hootguard/display/deactivate_display.py"])

def handle_display():
    global press_count
    start_time = time.time()
    with display_lock:
        if press_count == 1:
            display_ip_address()
        elif press_count == 2:
            display_snooze_time()
        elif press_count == 3:
            display_version()
            press_count = 0  # Reset press count to 0 to allow switching again

    while not stop_event.is_set():
        with display_lock:
            elapsed_time = time.time() - last_press_time
            if elapsed_time > 10:
                press_count = 0  # Reset press count to 0 to restart from 0 next time
                deactivate_display()
                break
        time.sleep(0.1)

def run_show_ip_address(channel):
    global last_press_time, press_count, display_thread, stop_event
    current_time = time.time()
    if current_time - last_press_time >= debounce_time:
        last_press_time = current_time
        with display_lock:
            press_count += 1

        if display_thread and display_thread.is_alive():
            stop_event.set()
            display_thread.join()

        stop_event.clear()
        display_thread = threading.Thread(target=handle_display)
        display_thread.start()

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=run_show_ip_address, bouncetime=200)

try:
    while True:
        time.sleep(0.1)  # Small sleep to prevent busy waiting
finally:
    GPIO.cleanup()
