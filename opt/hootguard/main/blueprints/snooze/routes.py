import os
import subprocess
import threading
import time
from flask import Blueprint, request, render_template, redirect
from scripts.snooze_read_status import snooze_read_status_and_return_status
from scripts.snooze_update_status_file import snooze_update_time

# --- OTHER SCRIPTS ---
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
ADBLOCK_STATUS_FILE = config['adblock']['snooze_status_path']
ADBLOCK_END_TIME_FILE = config['adblock']['snooze_end_time_path']

# Create the Snooze Blueprint
snooze_bp = Blueprint('snooze', __name__)

def read_adblock_status():
    """ Reads the adblock status file and returns 'active' or 'deactive'. """
    if os.path.exists(ADBLOCK_STATUS_FILE):
        with open(ADBLOCK_STATUS_FILE, "r") as file:
            status = file.read().strip().lower()
            logger.debug(f"Read status from file: '{status}'")
            return status if status in ["active", "deactive"] else "unknown"
    logger.debug("Adblock status file not found")
    return "unknown"

def write_adblock_status(status):
    """ Writes the new adblock status to the status file. """
    with open(ADBLOCK_STATUS_FILE, "w") as file:
        file.write(status)

def write_snooze_end_time(end_time):
    """ Stores the snooze end time in a file, ensuring it is never empty. """
    with open(ADBLOCK_END_TIME_FILE, "w") as file:
        file.write(str(end_time) if end_time > 0 else "0")

def read_snooze_end_time():
    """ Reads the stored snooze end time, returns 0 if file is empty or not set. """
    if os.path.exists(ADBLOCK_END_TIME_FILE):
        with open(ADBLOCK_END_TIME_FILE, "r") as file:
            content = file.read().strip()
            if content.isdigit():  # Ensures content is a valid number
                return(int(content))
    return 0  # Return 0 if file does not exist or is empty

def auto_reactivate_adblock(snooze_time):
    """ Waits for snooze_time seconds and then enables Pi-hole """
    time.sleep(snooze_time)  # Wait until the snooze period is over
    subprocess.run(["pihole", "enable"], check=True)
    write_adblock_status("active")
    logger.info(f"Auto-reenabled Ad Blocking after {snooze_time} seconds.")



# --- ROUTES ---

@snooze_bp.route('/snooze_settings', methods=['GET', 'POST'])
def snooze_settings():
        status_snooze = snooze_read_status_and_return_status() # Snooze time
        adblock_status = read_adblock_status()  # Read status from file (active / deactive)
        snooze_end_time = read_snooze_end_time()
        nts = request.args.get('nts')
        return render_template('snooze_settings.html', snooze_status=status_snooze, new_time_set=nts, adblock_status=adblock_status, snooze_end_time=snooze_end_time)
        # return render_template('snooze_settings.html', snooze_status=status_snooze, new_time_set=nts, adblock_status=adblock_status)


@snooze_bp.route('/snooze_change', methods=['GET', 'POST'])
def snooze_change():
        snooze_update_time(request.form['snooze_time'])
        return redirect('/snooze_settings?nts=True')


@snooze_bp.route('/snooze_activate_deactivate', methods=['POST'])
def snooze_activate_deactivate():
    try:
        action = request.form.get('adblock_action')
        snooze_time = snooze_read_status_and_return_status()

        if action == "disable":
            # Disable Ad Blocking
            subprocess.run(["pihole", "disable"], check=True)
            write_adblock_status("deactive")

            # Calculate and store the end time (Unix timestamp)
            snooze_end_time = int(time.time()) + snooze_time
            write_snooze_end_time(snooze_end_time)

            # Start a background thread to re-enable adblocking after snooze_time
            threading.Thread(target=auto_reactivate_adblock, args=(snooze_time,), daemon=True).start()
        
        elif action == "enable":
            # Enable Ad Blocking immediately
            subprocess.run(["pihole", "enable"], check=True)
            write_adblock_status("active")

            # Remove snooze time file if it exists
            if os.path.exists(ADBLOCK_END_TIME_FILE):
                os.remove(ADBLOCK_END_TIME_FILE)

        return redirect('/snooze_settings')

    except Exception as e:
        logger.error(f"Error in snooze_activate_deactivate: {e}")
        return redirect('/snooze_settings')
