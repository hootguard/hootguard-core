# Script Name: vpn_get_public_server_key.py
# Version: 0.3
# Author: HootGuard
# Date: 3. October 2024

# Description:
# This script retrieves the public key of a specified WireGuard interface (e.g., wg0 or wg1). It reads the public key 
# from a file located in the 'VPN_WIREGUARD_PATH' directory, which is defined in 'scripts.global_config'. The public 
# key is stored in a file named 'publickey_<interface>'.

import os
#from scripts.global_config import VPN_WIREGUARD_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_WIREGUARD_PATH = config['vpn']['wireguard_main_path']

def get_public_server_key(interface):
    """Retrieve the public key of the WireGuard interface (wg0 or wg1)."""
    # Define the file path based on the interface
    key_file = f"{VPN_WIREGUARD_PATH}/publickey_{interface}"
    
    # Read the public key from the file
    try:
        with open(key_file, 'r') as f:
            public_key = f.read().strip()
        logger.debug(f"Retrieved public key for {interface}: {public_key}")
        return public_key
    except IOError as e:
        logger.debug(f"Failed to retrieve public key for {interface}: {str(e)}")
        return None
