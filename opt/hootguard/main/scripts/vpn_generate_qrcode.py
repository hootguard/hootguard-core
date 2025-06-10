# Script Name: vpn_generate_qr_code.py
# Version: 0.7
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script generates a QR code for a specific VPN client's configuration. It checks whether the
# client's configuration file exists and attempts to create a corresponding QR code for it. The script 
# retries the operation up to a predefined number of times if the configuration file is not immediately 
# available. Once the QR code is successfully created, it sets the file permissions so that it can be 
# displayed on the HootGuard website. If the QR code generation fails after all retries, it returns False.

import os
import time
import qrcode
#from .global_config import VPN_CONFIGS_PATH, VPN_QRCODE_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_QRCODE_PATH = config['vpn']['client_qrcode_path']
VPN_CONFIGS_PATH = config['vpn']['client_configs_path']

def generate_qr_code(client_name, retries=2, delay=2):
    """
    Generates a QR code for the VPN client's configuration with retries.
    Retries until the configuration file exists or the maximum number of retries is reached.
    Returns True if successful, False otherwise.
    
    Parameters:
    client_name (str): The name of the client for whom the QR code is generated.
    retries (int): Number of retries if the configuration file is not found.
    delay (int): Delay in seconds between retries.
    """
    # Constructed paths
    config_file_path = os.path.join(VPN_CONFIGS_PATH, f'{client_name}.conf')
    qr_path = os.path.join(VPN_QRCODE_PATH, f'{client_name}_qr.png')

    # Check if the QR code directory exists, create it if necessary
    if not os.path.exists(VPN_QRCODE_PATH):
        logger.debug(f"QR code path {VPN_QRCODE_PATH} does not exist. Creating it now.")
        try:
            os.makedirs(VPN_QRCODE_PATH, exist_ok=True)
        except PermissionError as e:
            logger.error(f"Permission denied while creating {VPN_QRCODE_PATH}: {e}")
            return False

    # Retry logic
    for attempt in range(retries):
        if os.path.exists(config_file_path):
            try:
                with open(config_file_path, 'r') as config_file:
                    qr_content = config_file.read()
                    qr = qrcode.make(qr_content)
                    qr.save(qr_path)

                    # Set the permissions to 644 (-rw-r--r--) so the website can display the QR code
                    os.chmod(qr_path, 0o644)

                    logger.info(f"QR code for user {client_name} successfully generated on attempt {attempt + 1}.")
                    return True
            except (IOError, PermissionError) as e:
                logger.error(f"Failed to generate QR code for {client_name}: {e}")
        else:
            logger.warning(f"Configuration file for {client_name} not found. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
            time.sleep(delay)

    # Return False if the QR code generation fails after all retries
    logger.error(f"QR code for user {client_name} could not be created after {retries} attempts.")
    return False
