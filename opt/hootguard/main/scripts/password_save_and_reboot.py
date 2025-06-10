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
from cryptography.fernet import Fernet
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
PW_HASHED_PASSWORD_PATH = config['passwords']['hashed_password_path']
PW_ENCRYPTED_PASSWORD_PATH = config['passwords']['encrypted_password_path']
PW_SECRET_KEY_PATH = config['passwords']['secret_key_path']

def password_save_and_reboot_system(new_password, initial_setup=None):
    """Hash the new password, save it, and update the Pi-hole admin password."""
    logger.debug(f"INFO - Saving new password and rebooting system.")

    try:
        # Hash the password and save it
        new_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        with open(PW_HASHED_PASSWORD_PATH, 'w') as file:
            file.write(new_hash)
        logger.debug(f"INFO - New hashed password saved to {PW_HASHED_PASSWORD_PATH}")

        """ Encrypt the password and store it in a file. """
        # Load the encryption key
        with open(PW_SECRET_KEY_PATH, 'rb') as key_file:
            key = key_file.read()

        # Encrypt the password
        f = Fernet(key)
        encrypted_password = f.encrypt(new_password.encode())

        # Write the encrypted password to a file
        with open(PW_ENCRYPTED_PASSWORD_PATH, "wb") as file:
            file.write(encrypted_password)
        logger.info("Password encrypted and saved successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return False

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
        subprocess.call(['/usr/bin/sudo', 'reboot'])
    except Exception as e:
        logger.error(f"ERROR - Error during reboot: {e}")

#if __name__ == "__main__":
#    password_save_and_reboot_system("HootGuardSentry", initial_setup=True)
