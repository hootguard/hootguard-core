# Script Name: password_save_and_reboot.py
# Version: 0.2
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script securely updates the system password by hashing the new password and saving it to a file. 
# It also updates the Pi-hole admin password and reboots the system after the update. If the password update 
# fails, the script logs the error and prevents the reboot.

import subprocess
from werkzeug.security import generate_password_hash
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
PW_HASHED_PASSWORD_PATH = config['passwords']['hashed_password_path']

def password_save_and_reboot_system(new_password, initial_setup=None):
    """Hash the new password, save it, and update the Pi-hole admin password."""
    logger.debug(f"INFO - Saving new password and rebooting system.")

    new_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    with open(PW_HASHED_PASSWORD_PATH, 'w') as file:
        file.write(new_hash)
    logger.debug(f"INFO - New hashed password saved to {PW_HASHED_PASSWORD_PATH}")

    # Update Pi-hole admin password
    try:
        subprocess.check_call(['pihole', '-a', '-p', new_password])
        logger.info("INFO - Pi-hole password successfully updated.")
        if not initial_setup:
            # Reboot the system after successful password update
            reboot_system()
        else:
            logger.info("INFO - Initial setup detected. Skipping system reboot after password update.")
            return True  # Password successfully updated, for initial setup main script
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR - Error updating Pi-hole password: {e}")
        # Handle error (redirect to an error page or display a message)

def reboot_system():
    """Reboot the system to apply the new configuration."""
    try:
        logger.info("INFO - Rebooting the system.")
        # Execute the reboot command
        subprocess.call(['sudo', 'reboot'])
    except Exception as e:
        logger.error(f"ERROR - Error during reboot: {e}")
