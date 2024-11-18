# Script Name: vpn_create_client_config.py
# Version: 0.4
# Author: HootGuard
# Date: 3. October 2024

# Description:
# This script creates a WireGuard client configuration file based on the provided client details, such as the 
# private key, IP addresses, DNS servers, and peer (server) information. The configuration is saved in the 
# directory specified by the 'VPN_CONFIGS_PATH' from the global configuration. The script checks if the directory exists, 
# creates it if needed, and saves the configuration file as <client_name>.conf.

import os
#from scripts.global_config import VPN_CONFIGS_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CONFIGS_PATH = config['vpn']['client_configs_path']


def create_client_config(client_name, client_priv_key, ipv4_address, ipv6_address, primary_dns, secondary_dns, server_pub_key, client_psk, endpoint, port):
    """Create the client configuration file and save it to /opt/hootguard/pivpn/configs/<clientname>.conf"""
    
    # Define the path for the client config file
    config_file = os.path.join(VPN_CONFIGS_PATH, f"{client_name}.conf")
    
    # Check if the directory exists, if not, create it
    if not os.path.exists(VPN_CONFIGS_PATH):
        try:
            os.makedirs(config_dir, exist_ok=True)
            logger.debug(f"Directory {VPN_CONFIGS_PATH} created.")
        except OSError as e:
            logger.debug(f"Failed to create directory {VPN_CONFIGS_PATH}: {str(e)}")
            return False

    # Create the client configuration content (removing the leading newline)
    config_content = (
        f"[Interface]\n"
        f"PrivateKey = {client_priv_key}\n"
        f"Address = {ipv4_address}/24,{ipv6_address}\n"
        f"DNS = {primary_dns}\n\n"
        f"[Peer]\n"
        f"PublicKey = {server_pub_key}\n"
        f"PresharedKey = {client_psk}\n"
        f"Endpoint = {endpoint}:{port}\n"
        f"AllowedIPs = 0.0.0.0/0, ::/0\n"
    )

    # Write the content to the client config file
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        logger.debug(f"Client configuration for {client_name} saved to {config_file}")
        return True
    except IOError as e:
        logger.debug(f"Failed to write client configuration for {client_name}: {str(e)}")
        return False
