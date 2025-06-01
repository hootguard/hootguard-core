import RPi.GPIO as GPIO
import requests
import time
import subprocess
from RPLCD.i2c import CharLCD
import threading

# GPIO setup for button
BUTTON_PIN = 17  # GPIO pin for the button

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Snooze timer - File to store and read snooze time
TIMER_FILE = '/opt/hootguard/snooze/snooze-time.txt'
snooze_active = False  # Global variable to track snooze state
snooze_thread = None  # Thread for snooze display

# LCD setup
I2C_ADDR = 0x27
lcd = CharLCD(i2c_expander='PCF8574', address=I2C_ADDR, port=3,
              cols=16, rows=2, dotsize=8,
              charmap='A02', auto_linebreaks=True,
              backlight_enabled=True)  # Enable backlight initially

def get_local_ip_address():
    """Get the current local IP address of the Raspberry Pi."""
    try:
        ip_address = subprocess.check_output(['hostname', '-I']).decode().strip().split(' ')[0]
        return ip_address
    except Exception as e:
        print(f"Error obtaining local IP: {e}")
        return "127.0.0.1"

PIHOLE_IP = get_local_ip_address()  # Get and store the local IP address of the Pi

def get_webpassword():
    """Get the current web password for Pi-hole from the system configuration file."""
    try:
        output = subprocess.check_output("cat /etc/pihole/setupVars.conf | grep WEBPASSWORD", shell=True).decode().strip()
        webpassword = output.split('=')[1]  # Extract the password from the output
        return webpassword
    except Exception as e:
        print(f"Error obtaining web password: {e}")
        return None

def get_snooze_time():
    """Read the snooze time setting from a file."""
    try:
        with open(TIMER_FILE, 'r') as file:
            return int(file.read().strip())  # Read and return the snooze time
    except FileNotFoundError:
        return 300  # Return default value if file not found

def update_display(snooze_time_remaining):
    lcd.clear()
    lcd.write_string("Snooze active")
    lcd.crlf()
    minutes = snooze_time_remaining // 60
    seconds = snooze_time_remaining % 60
    lcd.write_string(f"{minutes}m {seconds}s left")

def show_snooze_status():
    snooze_time = get_snooze_time()
    start_time = time.time()
    end_time = start_time + snooze_time

    while time.time() < end_time and snooze_active:
        remaining_time = int(end_time - time.time())
        update_display(remaining_time)
        time.sleep(10)  # Update every 10 seconds

    lcd.clear()
    lcd.backlight_enabled = False

def activate_snooze():
    global snooze_active, snooze_thread
    auth = get_webpassword()  # Retrieve the current web password
    if not auth:
        print("Failed to retrieve web password. Cannot deactivate Pi-hole.")
        return

    snooze_time = get_snooze_time()  # Get the snooze time
    url = f"http://{PIHOLE_IP}/admin/api.php?disable={snooze_time}&auth={auth}"  # Construct the URL for the API request
    requests.get(url)  # Send the request to deactivate Pi-hole

    snooze_active = True
    # Start the snooze display in a new thread
    snooze_thread = threading.Thread(target=show_snooze_status)
    snooze_thread.start()

def deactivate_snooze():
    global snooze_active, snooze_thread
    auth = get_webpassword()  # Retrieve the current web password
    if not auth:
        print("Failed to retrieve web password. Cannot reactivate Pi-hole.")
        return

    url = f"http://{PIHOLE_IP}/admin/api.php?enable&auth={auth}"  # Construct the URL for the API request
    requests.get(url)  # Send the request to reactivate Pi-hole

    snooze_active = False
    if snooze_thread:
        snooze_thread.join()  # Wait for the snooze display thread to finish

def button_pressed_callback(channel):
    global snooze_active
    if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # Check if button is actually pressed
        if snooze_active:
            deactivate_snooze()
        else:
            activate_snooze()

# Add event detection for button press
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_pressed_callback, bouncetime=500)

print("Waiting for button press...")

try:
    while True:
        time.sleep(1)  # Main loop to keep the script running
except KeyboardInterrupt:
    pass  # Handle Ctrl+C gracefully
finally:
    GPIO.cleanup()  # Clean up GPIO on exit
