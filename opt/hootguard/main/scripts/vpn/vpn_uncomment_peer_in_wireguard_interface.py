# Script Name: vpn_uncomment_peer_in_wireguard_interface.py
# Version: 0.1
# Author: HootGuard
# Date: 5. October 2024

# Description:
# this script eddifiently activates tthe VPN client.
# This script uncomments the peer configuration for a VPN client in the WireGuard config file.

import subprocess
#from scripts.global_config import VPN_WIREGUARD_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_WIREGUARD_PATH = config['vpn']['wireguard_main_path']

def uncomment_peer_in_wg_config(client_name, interface):
    """Uncomment the peer configuration for the client in the WireGuard config file."""
    config_file = f"{VPN_WIREGUARD_PATH}/{interface}.conf"

    # Use the hootguard script to uncomment the client configuration
    try:
        result = subprocess.run(
            [
                '/usr/bin/sudo', '/usr/local/bin/hootguard', 'uncomment-peer',
                config_file, client_name
            ],
            capture_output=True,
            text=True,
            check=True
        )
        logger.debug(f"SUCCESS - Peer configuration for VPN client {client_name} uncommented in {config_file}.")
        return True
    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Failed to uncomment peer configuration for VPN client {client_name} in {config_file}: {str(e)}")
        return False
