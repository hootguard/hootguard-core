# Script Name: adblock_update_status_file.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script manages the Adblock status file and updates the Pi-hole blocking lists accordingly in the HootGuard system.
# It reads the current status from the Adblock status file, updates the status based on user selections, and 
# triggers an update to the Pi-hole blocklists. The script also handles form data submitted via a Flask app to 
# change Adblock profiles.

import os
from .adblock_add_delete_blocking_lists_from_gravity_db import adblock_add_blocking_list
#from .global_config import ADBLOCK_STATUS_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
ADBLOCK_STATUS_PATH = config['adblock']['status_path']

def adblock_read_status_file():
    """Read the Adblock status file and return the active profiles."""
    logger.debug(f"INFO - Reading Adblock status from {ADBLOCK_STATUS_PATH}")
    status = {
        "normal": False,
        "enhanced": False,
        "max": False,
        "adult": False,
        "gambling": False,
        "social": False
    }
    if os.path.exists(ADBLOCK_STATUS_PATH):
        with open(ADBLOCK_STATUS_PATH, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line in status:
                    status[line] = True
        logger.debug(f"INFO - Adblock status read: {status}")
    else:
        logger.debug(f"ERROR - Adblock status file not found.")
    return status

def update_status_file(profiles):
    """Update the Adblock status file and apply the new blocking profiles."""
    logger.debug(f"INFO - Updating Adblock status file with profiles: {profiles}")
    with open(ADBLOCK_STATUS_PATH, "w") as file:
        for profile in profiles:
            file.write(profile + "\n")
    logger.debug(f"SUCCESS - Adblock status file updated. Updating blocking lists.")
    adblock_add_blocking_list(profiles)


def adblock_profile_change(form_data):
    """Handle Adblock profile changes based on form data."""
    profiles = ["normal", "enhanced", "max", "adult", "gambling", "social"]
    active_profiles = []
    
    radio_selection = form_data.get('adblock_profile')
    if radio_selection in ["normal", "enhanced", "max"]:
        active_profiles.append(radio_selection)

    # Checking checkboxes
    for profile in ["adult", "gambling", "social"]:
        if form_data.get(profile) == 'on':
            active_profiles.append(profile)

    logger.debug(f"INFO - Active profiles selected: {active_profiles}")
    update_status_file(active_profiles)





