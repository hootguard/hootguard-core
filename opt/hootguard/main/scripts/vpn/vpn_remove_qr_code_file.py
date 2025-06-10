# Script Name: vpn_remove_qr_code_file.py
# Version: 0.1
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script deletes the QR code file associated with a VPN client. It constructs the path to the client's QR code file,
# checks if the file exists, and removes it. If the file doesn't exist or an error occurs during deletion, appropriate messages are logged.

import os
#from scripts.global_config import VPN_QRCODE_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_QRCODE_PATH = config['vpn']['client_qrcode_path']

def remove_qr_code(client_name):
    """Delete the QR code file for the VPN client."""
    # Construct the path to the QR code file
    qr_code_file = os.path.join(VPN_QRCODE_PATH, f'{client_name}_qr.png')

    # Check if the QR code file exists and remove it
    if os.path.exists(qr_code_file):
        try:
            os.remove(qr_code_file)
            logger.debug(f"SUCCESS - QR code file for {client_name} removed successfully.")
            return True
        except OSError as e:
            logger.debug(f"ERROR - Failed to remove QR code file for {client_name}: {str(e)}")
            return False
    else:
        logger.debug(f"ERROR - QR code file for {client_name} does not exist.")
        return False
