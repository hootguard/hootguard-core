# Script Name: vpn_remove_peer_from_wg_config.py
# Version: 0.1
# Author: HootGuard
# Date: 4. October 2024

# Description:
# This script removes the peer (client) configuration from the WireGuard configuration file for a specified interface.
# The peer configuration is identified by the '### begin <client_name> ###' and '### end <client_name> ###' markers.

import subprocess
#from scripts.global_config import VPN_WIREGUARD_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_WIREGUARD_PATH = config['vpn']['wireguard_main_path']

def remove_peer_from_wg_config(client_name, interface):
    """Remove the peer configuration from the WireGuard config (wg0.conf or wg1.conf)."""
    config_file = f"{VPN_WIREGUARD_PATH}/{interface}.conf"

    # Use sed to remove the lines between '### begin <client_name> ###' and '### end <client_name> ###'
    try:
        result = subprocess.run(
            [
                '/usr/bin/sudo', '/usr/local/bin/hootguard', 'remove-peer',
                config_file, client_name
            ],
            capture_output=True,
            text=True,
            check=True
        )
        logger.debug(f"SUCCESS - Peer configuration for {client_name} removed from {config_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Failed to remove peer configuration for {client_name} from {config_file}: {str(e)}")
        return False
