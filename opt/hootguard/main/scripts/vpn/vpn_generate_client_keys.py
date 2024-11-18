# Script Name: vpn_generate_client_keys.py
# Version: 1.0
# Author: HootGuard
# Date: 3. October 2024

# Description:
# This script generates a WireGuard private key, public key, and preshared key for a given client. It saves the keys 
# in the directory specified by 'VPN_CLIENT_KEYS_PATH', ensuring they are created with secure file permissions 
# (read/write for the owner, no execute permissions). The generated keys are returned by the function.

import os
import subprocess
#from scripts.global_config import VPN_CLIENT_KEYS_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENT_KEYS_PATH = config['vpn']['client_keys_path']

# Set umask to ensure files are created with read/write but no execute permissions
os.umask(0o117)

def generate_keys(client_name):
    """Generate WireGuard private key, public key, and preshared key for a client."""
    try:
        # File paths for the keys
        priv_key_file = os.path.join(VPN_CLIENT_KEYS_PATH, f"{client_name}_priv")
        pub_key_file = os.path.join(VPN_CLIENT_KEYS_PATH, f"{client_name}_pub")
        psk_file = os.path.join(VPN_CLIENT_KEYS_PATH, f"{client_name}_psk")

        # Generate private key
        priv_key = subprocess.check_output("wg genkey", shell=True).decode('utf-8').strip()
        with open(priv_key_file, 'w') as f:
            f.write(priv_key)
        logger.debug(f"Private key generated and saved to {priv_key_file}")

        # Generate public key from private key
        pub_key = subprocess.check_output(f"echo {priv_key} | wg pubkey", shell=True).decode('utf-8').strip()
        with open(pub_key_file, 'w') as f:
            f.write(pub_key)
        logger.debug(f"Public key generated and saved to {pub_key_file}")

        # Generate preshared key
        psk = subprocess.check_output("wg genpsk", shell=True).decode('utf-8').strip()
        with open(psk_file, 'w') as f:
            f.write(psk)
        logger.debug(f"Preshared key generated and saved to {psk_file}")

        #return True
        return priv_key, pub_key, psk
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to generate keys for client {client_name}: {str(e)}")
        return False
