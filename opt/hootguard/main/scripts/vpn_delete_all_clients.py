# Script Name: vpn_delete_all_clients.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script removes all VPN clients and their associated QR code files in the HootGuard system.
# It performs the following actions:
# - Deletes all VPN client configurations using the `pivpn -r` command with automatic confirmation.
# - Deletes all QR code PNG files located in the specified directory from the global configuration.
# - Logs success or failure for each deletion operation.
# If any error occurs during the process, the script logs the issue and exits with a failure status.


import subprocess
import os
import glob
import logging
#from .global_config import VPN_QRCODE_PATH
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_QRCODE_PATH = config['vpn']['client_qrcode_path']

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

def delete_all_vpn_clients_and_qrcodes():
    """
    Delete all existing VPN clients and all PNG files in the /opt/hootguard/static/ directory.
    Returns True if successful, False otherwise.
    """
    try:
        # Find all PNG files in the directory
        png_files = glob.glob(os.path.join(VPN_QRCODE_PATH, '*_qr.png'))
        
        # Extract client names from the filenames
        clients = [os.path.basename(f).replace('_qr.png', '') for f in png_files]
        
        for client in clients:
            try:
                # Delete the VPN client non-interactively by automatically confirming deletion
                subprocess.run(['pivpn', '-r', client, '-y'], check=True)
            except subprocess.CalledProcessError as e:
                logging.error(f"Error during the deletion process: {e}")
                return False

        # Delete all PNG files in the /opt/hootguard/static/ directory
        for png_file in png_files:
            try:
                os.remove(png_file)
            except OSError as e:
                logging.error(f"Error during the deletion process: {e}")
                return False

        logging.info("All clients successfully deleted.")
        return True
    except Exception as e:
        logging.error(f"Error during the deletion process: {e}")
        return False
