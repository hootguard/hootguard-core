# Script Name: vpn_comment_out_peer_in_wireguard_interface.py
# Version: 0.1
# Author: HootGuard
# Date: 5. October 2024

# Description:
# This script deactivates a VPN client by commenting out the peer configuration for the client in the WireGuard configuration file.
# The script identifies the client's configuration block in the WireGuard config file (wg0 or wg1) by locating the markers
# '### begin <client_name> ###' and '### end <client_name> ###', then uses the 'sed' command to comment out the lines in between.
# This effectively disables the VPN client without removing its configuration.

import subprocess
#from scripts.global_config import VPN_WIREGUARD_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_WIREGUARD_PATH = config['vpn']['wireguard_main_path']

def comment_out_peer_in_wg_config(client_name, interface):
    """Comment out the peer configuration for the client in the WireGuard config file."""
    config_file = f"{VPN_WIREGUARD_PATH}/{interface}.conf"

    # Use sed to comment out the lines between '### begin <client_name> ###' and '### end <client_name> ###'
    try:
        # Call the 'hootguard' command to comment out the peer configuration
        subprocess.run(
            [
                '/usr/bin/sudo',
                '/usr/local/bin/hootguard',
                'comment-peer',
                config_file,
                client_name,
            ],
            check=True,
        )
        logger.debug(f"Peer configuration for VPN client {client_name} commented out in {config_file}.")
        return True
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to comment out peer configuration for VPN client {client_name} in {config_file}: {str(e)}")
        return False
