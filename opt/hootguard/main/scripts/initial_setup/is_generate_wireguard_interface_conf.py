# Script Name: is_generate_wireguard_interface_conf.py
# Version: 0.2
# Author: HootGuard
# Date: 02. December 2024

# Description:
# This script generates a WireGuard configuration file for a specified interface (e.g., wg0, wg1).
# It retrieves the WireGuard configuration directory path from the global configuration and:
# - Creates the configuration file with interface-specific settings, including the private key, IP addresses, MTU, and port.
# - Sets the file ownership to `root:root` and permissions to `600` for security.
# - Logs the success or failure of the operation and clears the private key from memory upon completion.
# Returns True if successful, False otherwise.

import os
import sys
import subprocess
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Define the path where WireGuard configuration files are stored
WG_CONF_DIRECTORY = config['vpn']['wireguard_main_path']

def create_wireguard_conf(wg_interface, private_key, ipv4_address, ipv6_address):
    """Creates a WireGuard configuration file for the specified interface and sets file permissions."""
    
    # Define the file path for the WireGuard configuration
    wg_conf_file = os.path.join(WG_CONF_DIRECTORY, f"{wg_interface}.conf")

    # Determine the ListenPort based on the interface
    listen_port = 51820 if wg_interface == "wg0" else 51821

    # Create the configuration content
    conf_content = f"""[Interface]
PrivateKey = {private_key}
Address = {ipv4_address}/24,{ipv6_address}/64
MTU = 1420
ListenPort = {listen_port}
"""

    try:
        # Write the configuration to the file
        with open(wg_conf_file, 'w') as conf_file:
            conf_file.write(conf_content)

        # Use the hootguard script to set ownership and permissions
        # Change the ownership to root:root
        ownership_command = [
            '/usr/bin/sudo',
            '/usr/local/bin/hootguard',
            'set-file-ownership',
            wg_conf_file,
            'root',
            'root'
        ]
        # Set the permissions to 600 (rw for owner only)
        permissions_command = [
            '/usr/bin/sudo',
            '/usr/local/bin/hootguard',
            'set-file-permissions',
            wg_conf_file,
            '600'
        ]

        subprocess.check_call(ownership_command)
        subprocess.check_call(permissions_command)

        logger.info(f"WireGuard configuration file created: {wg_conf_file}")
        return True
    except Exception as e:
        logger.debug(f"Error creating WireGuard configuration: {e}")
        return False
    finally:
        # Clear the private key from memory by setting it to None
        private_key = None
        logger.info(f"Private key cleared from memory for interface {wg_interface}.")
