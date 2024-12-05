# Script Name: reset_delete_wg_keys_and_configs.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script deletes WireGuard private keys, public keys, and configuration files in the HootGuard system.
# - Identifies files to delete based on paths from the global configuration.
# - Deletes private keys, public keys, and WireGuard configuration files for interfaces (e.g., wg0, wg1).
# - Logs or prints the status of each deletion, marking success or failure.
# Ensures secure cleanup of WireGuard credentials and configurations during system reset or reconfiguration.
# Returns `True` if all files are successfully deleted, `False` otherwise.

import os
import pwd
import grp
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()


files_to_delete = [
    config['vpn']['wireguard_wg0_privatekey_path'],
    config['vpn']['wireguard_wg1_privatekey_path'],
    config['vpn']['wireguard_wg0_publickey_path'],
    config['vpn']['wireguard_wg1_publickey_path'],
    os.path.join(config['vpn']['wireguard_main_path'], f"{config['vpn']['wireguard_interface_1']}.conf"),
    os.path.join(config['vpn']['wireguard_main_path'], f"{config['vpn']['wireguard_interface_2']}.conf")
]

# Function to delete the files
def delete_wg_keys_and_configs():
    success = True
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)  # Delete the file
                print(f"Deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
                success = False  # Mark failure if a file is not found
        except Exception as e:
            print(f"Error occurred while processing {file_path}: {e}")
            success = False  # Mark failure if an error occurs

    return True  # Return True if successful, False otherwise
