# Script Name: vpn_remove_client_keys.py
# Version: 0.1
# Author: HootGuard
# Date: 4. October 2024

# Description:
# This script deletes the WireGuard private key, public key, and preshared key for a given client.
# It ensures that the keys are securely deleted from the directory specified by 'VPN_CLIENT_KEYS_PATH'.

import os
#from scripts.global_config import VPN_CLIENT_KEYS_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENT_KEYS_PATH = config['vpn']['client_keys_path']

def remove_client_keys(client_name):
    """Remove the client keys (private key, public key, preshared key) from the system."""
    
    # Define the paths for the keys
    priv_key_file = os.path.join(VPN_CLIENT_KEYS_PATH, f"{client_name}_priv")
    pub_key_file = os.path.join(VPN_CLIENT_KEYS_PATH, f"{client_name}_pub")
    psk_file = os.path.join(VPN_CLIENT_KEYS_PATH, f"{client_name}_psk")

    # Function to safely remove the key files
    def remove_key_file(key_file, key_name):
        if os.path.exists(key_file):
            try:
                os.remove(key_file)
                logger.debug(f"SUCCESS - {key_name} for {client_name} removed.")
            except OSError as e:
                logger.debug(f"ERROR - Failed to remove {key_name} for {client_name}: {str(e)}")
                return False
        else:
            logger.debug(f"ERROR - {key_name} for {client_name} does not exist.")
        return True

    # Remove the private key, public key, and preshared key
    success_priv = remove_key_file(priv_key_file, "Private key")
    success_pub = remove_key_file(pub_key_file, "Public key")
    success_psk = remove_key_file(psk_file, "Preshared key")

    # Return True only if all keys were successfully removed
    return success_priv and success_pub and success_psk
