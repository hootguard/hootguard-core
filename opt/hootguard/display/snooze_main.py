# Script Name: snooze_main.py
# Version: 0.2
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script manages the snooze functionality, including toggling Pi-hole snooze, updating LED status,
# and handling button presses to activate or deactivate snooze.

import RPi.GPIO as GPIO
import subprocess
import threading
import time
import logging
import sys

# Add the path to global_config_loader.py
sys.path.append('/opt/hootguard/main/scripts')
from global_config_loader import load_config  # Import load_config function

# Load the global configuration
config = load_config()
SNOOZE_STATUS_FILE_PATH = config['misc']['snooze_status_file']
SNOOZE_TIME_FILE_PATH = config['misc']['snooze_time_file']

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# Pin Setup
BUTTON_PIN = 7  # GPIO 7 (Pin 26)
LED_PIN = 16    # GPIO pin for the LED

GPIO.setmode(GPIO.BCM)  # BCM = GPIO numbering (BOARD = pin numbering)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

# Global variables
last_press_time = 0
debounce_time = 0.25  # 250 milliseconds
#status_file = '/opt/hootguard/snooze/snooze-status.txt'
toggle_lock = threading.Lock()
stop_event = threading.Event()
snooze_thread = None

def initialize_snooze_status():
    """Initialize the snooze status to inactive on startup."""
    with open(SNOOZE_STATUS_FILE_PATH, 'w') as file:
        file.write('inactive')

def read_snooze_status():
    """Read the current snooze status from a file."""
    try:
        with open(SNOOZE_STATUS_FILE_PATH, 'r') as file:
            status = file.read().strip()
            return status == 'active'
    except FileNotFoundError:
        return False  # Default to inactive if file not found

def write_snooze_status(active):
    """Write the current snooze status to a file."""
    with open(SNOOZE_STATUS_FILE_PATH, 'w') as file:
        file.write('active' if active else 'inactive')

def toggle_snooze():
    global snooze_thread
    with toggle_lock:
        if read_snooze_status():
            logging.info("Snooze is active, deactivating now")
            stop_event.set()  # Signal the snooze thread to stop
            if snooze_thread:
                snooze_thread.join()  # Wait for the snooze thread to finish
            try:
                stop_event.clear()
                subprocess.run(["/usr/bin/python3", "/opt/hootguard/display/snooze_deactivate.py"])
            except Exception as e:
                logging.error(f"Error deactivating snooze: {e}")
        else:
            logging.info("Snooze is inactive, activating now")
            stop_event.clear()
            snooze_thread = threading.Thread(target=manage_led)
            snooze_thread.start()
            try:
                subprocess.run(["/usr/bin/python3", "/opt/hootguard/display/snooze_activate.py"])
                write_snooze_status(True)
            except Exception as e:
                logging.error(f"Error activating snooze: {e}")

def deactivate_display():
    """Deactivate the display."""
    subprocess.run(["/usr/bin/python3", "/opt/hootguard/display/deactivate_display.py"])

def handle_display():
    """Handle the display deactivation after a period of inactivity."""
    while not stop_event.is_set():
        elapsed_time = time.time() - last_press_time
        if elapsed_time > 5:
            deactivate_display()
            break
        time.sleep(0.1)


def button_callback(channel):
    global last_press_time
    current_time = time.time()
    if current_time - last_press_time >= debounce_time:
        last_press_time = current_time
        stop_event.set()  # Stop the current handle_display thread if running
        stop_event.clear()
        threading.Thread(target=handle_display).start()
        threading.Thread(target=toggle_snooze).start()

def manage_led():
    """Manage the LED based on the snooze time."""
    try:
        snooze_time = int(get_snooze_time())  # Get the snooze time as an integer
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on the LED
        start_time = time.time()
        while time.time() - start_time < snooze_time + 2:
            if stop_event.is_set():
                break
            time.sleep(0.1)
        GPIO.output(LED_PIN, GPIO.LOW)  # Turn off the LED
    finally:
        update_snooze_status("inactive")

def get_snooze_time():
    """Read the snooze time setting from a file."""
    try:
        with open(SNOOZE_TIME_FILE_PATH, 'r') as file:
            return file.read().strip()  # Read and return the snooze time
    except FileNotFoundError:
        return "300"  # Return default value if file not found

def update_snooze_status(status):
    """Update the snooze status file."""
    try:
        with open(SNOOZE_STATUS_FILE_PATH, 'w') as file:
            file.write(status)
    except Exception as e:
        logging.error(f"Error updating snooze status: {e}")

# Initialize snooze status on startup
initialize_snooze_status()

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)  # Increased bouncetime

try:
    while True:
        time.sleep(0.1)  # Small sleep to prevent busy waiting
finally:
    GPIO.cleanup()
