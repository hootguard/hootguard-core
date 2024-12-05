# Script Name: is_generate_wireguard_keys.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script generates private and public keys for a specified WireGuard interface and saves them securely.
# - The private key is saved in the WireGuard configuration directory with `root:root` ownership and `600` permissions.
# - The public key is generated using the private key and saved with `root:wireguard` ownership and `770` permissions.
# The script ensures secure storage and ownership of keys, logs the process, and clears sensitive data from memory after use.
# Returns the private key as a string for further use or `None` in case of errors.


import os
import subprocess
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Define the path where WireGuard configuration files are stored
WG_CONF_DIRECTORY = config['vpn']['wireguard_main_path']

def generate_wireguard_keys(interface_name):
    """Generates private and public keys for the specified interface and saves them in /etc/wireguard/."""
    
    # Define file paths for the private and public keys
    private_key_file = os.path.join(WG_CONF_DIRECTORY, f"privatekey_{interface_name}")
    public_key_file = os.path.join(WG_CONF_DIRECTORY, f"publickey_{interface_name}")
    
    private_key = None
    public_key = None

    try:
        # Generate the private key
        private_key = subprocess.check_output(['/usr/bin/wg', 'genkey']).strip()
        
        # Save the private key to a file
        with open(private_key_file, 'wb') as pk_file:
            pk_file.write(private_key)
        
        # Generate the public key using the private key
        public_key = subprocess.check_output(['/usr/bin/wg', 'pubkey'], input=private_key)
        
        # Save the public key to a file
        with open(public_key_file, 'wb') as pub_file:
            pub_file.write(public_key)

        # Use the hootguard script to set ownership and permissions
        # Change the ownership for private key to root:root
        ownership_command_private = [
            '/usr/bin/sudo',
            '/usr/local/bin/hootguard',
            'set-file-ownership',
            private_key_file,
            'root',
            'root'
        ]
        # Change the ownership for public key to root:wireguard
        ownership_command_public = [
            '/usr/bin/sudo',
            '/usr/local/bin/hootguard',
            'set-file-ownership',
            public_key_file,
            'root',
            'wireguard'
        ]
        subprocess.check_call(ownership_command_private)
        subprocess.check_call(ownership_command_public)


        # Set the permissions to 600 for private key
        permissions_command_private_key = [
            '/usr/bin/sudo',
            '/usr/local/bin/hootguard',
            'set-file-permissions',
            private_key_file,
            '600'
        ]
        # Set the permissions to 770 for public key
        permissions_command_public_key = [
            '/usr/bin/sudo',
            '/usr/local/bin/hootguard',
            'set-file-permissions',
            public_key_file,
            '770'
        ]
        subprocess.check_call(permissions_command_private_key)
        subprocess.check_call(permissions_command_public_key)

        logger.debug(f"Private and public keys generated and saved for interface {interface_name}")
        return private_key.decode()  # Return the private key as a string for further use
    except Exception as e:
        logger.debug(f"Error generating keys for interface {interface_name}: {e}")
        return None
    finally:
        # Ensure private and public key variables are cleared from memory
        private_key = None
        public_key = None
        logger.debug(f"Private and public key variables cleared for interface {interface_name}")
