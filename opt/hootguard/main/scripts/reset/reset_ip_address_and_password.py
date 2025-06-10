# Script Name: reset_ip_address_and_password.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script resets the IP address and passwords for the HootGuard system to their default settings.
# - Resets the IP configuration to DHCP by replacing the current `dhcpcd.conf` with its original backup.
# - Resets the web password by replacing it with the default hashed password file.
# - Decrypts and applies the default Pi-hole password using the secret key and encrypted password file.
# Logs the success or failure of each operation, ensuring a secure and functional reset process.
# Returns `True` if both IP and passwords are successfully reset, `False` otherwise.

import shutil
import subprocess
from cryptography.fernet import Fernet

from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
NW_DHCPCD_PATH = config['dhcp']['dhcpcd_path']
NW_DHCPCD_ORIGINAL_PATH = config['dhcp']['dhcpcd_original_path']
PW_HASHED_PASSWORD_PATH = config['passwords']['hashed_password_path']
PW_HASHED_DEFAULT_PASSWORD_PATH = config['passwords']['hashed_default_password_path']
PW_ENCRYPTED_PASSWORD_PATH = config['passwords']['encrypted_password_path']
PW_SECRET_KEY_PATH = config['passwords']['secret_key_path']

def reset_ip_and_password():
    if not reset_ip_address():
        logger.info("ERROR - Failed to reset the ip address")
        return False
    if not reset_passwords():
        logger.info("ERROR - Failed to reset web and pi-hole password")
        return False

    logger.info("IP address and password successfully reset")
    return True

def reset_ip_address():
    """Reset the IP address configuration to DHCP."""
    try:
        # Use hootguard to replace the dhcpcd.conf file
        subprocess.run(
            ['/usr/bin/sudo', '/usr/local/bin/hootguard', 'reset-ip', NW_DHCPCD_ORIGINAL_PATH, NW_DHCPCD_PATH],
            check=True
        )        
        logger.info("IP address reset to DHCP successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reset IP address: {e}")
        return False


def reset_passwords():
    default_password = "HootGuardSentry"

    try:
        # Reset web password
        shutil.copy(PW_HASHED_DEFAULT_PASSWORD_PATH, PW_HASHED_PASSWORD_PATH)
        logger.info("INFO - Web password reset successfully.")

        # Reset Pi-hole password
        with open(PW_ENCRYPTED_PASSWORD_PATH, 'rb') as file:
            encrypted_password = file.read()
        with open(PW_SECRET_KEY_PATH, 'rb') as file:
            key = file.read()

        # Encrypt the password
        f = Fernet(key)
        encrypted_password = f.encrypt(default_password.encode())

       # Write the encrypted password to a file
        with open(PW_ENCRYPTED_PASSWORD_PATH, "wb") as file:
            file.write(encrypted_password)

        # Run the pihole command and capture both stdout and stderr
        result = subprocess.run(
            ['pihole', '-a', '-p', default_password], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        # Combine stdout and stderr for easier checking
        combined_output = result.stdout + result.stderr

        # Check if the word 'error' or any similar error message is present
        if "error" in combined_output.lower():
            logger.info(f"ERROR - Failed to reset Pi-hole password: {combined_output}")
            return False
        else:
            logger.info(f"SUCCESS - Pi-hole password reset successfully. Output: {combined_output}")
            return True

    except Exception as e:
        logger.info(f"ERROR - Failed to reset passwords: {e}")
        return False
