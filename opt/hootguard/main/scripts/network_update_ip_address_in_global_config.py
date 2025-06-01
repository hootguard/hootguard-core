# Script Name: network_update_ip_address_in_global_config.py
# Version: 0.3
# Author: HootGuard
# Date: 11. January 2025

# Description:
# This script updates the Interface 1 ip address (normally eth0) in the global YAML configuration file used by the HootGuard system.
# It reads the YAML file, updates the corresponding ip address entry with the new ip address, and writes the changes back to the file.
# The script includes error handling to manage any issues during the file reading and writing process.
# This script also extracts the network address from the ip address and stores it in the global config.

import yaml
import ipaddress
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
GLOBAL_CONFIG_FILE_PATH = config['misc']['global_config_file']

# Function to calculate the network address from an IP address and subnet mask
def calculate_network(ip_address):
    """Calculate the network address for a given IP address with CIDR."""
    try:
        return str(ipaddress.IPv4Interface(ip_address).network)
    except Exception as e:
        logger.error(f"ERROR - Failed to calculate network address: {str(e)}")
        raise

# Function to replace the VPN endpoint in the YAML config file
def replace_network_ip_address(ip_version, ip_address, primary_dns_ip_address=None):
    """Replace the VPN endpoint in the YAML configuration file."""
    try:
        logger.debug(f"INFO - Replacing ip addess in {GLOBAL_CONFIG_FILE_PATH} with : {ip_address}")

        # Read the YAML configuration file
        with open(GLOBAL_CONFIG_FILE_PATH, 'r') as file:
            config = yaml.safe_load(file)

        # Update the ip address in the global_config.yaml file
        if ip_version == "ipv4":
            config['network']['interface_1_v4_ip_address'] = ip_address
            config['network']['primary_dns'] = primary_dns_ip_address
            # Calculate and update the network address
            network = calculate_network(ip_address)
            config['network']['interface_1_v4_network'] = network
            logger.debug(f"INFO - Updated network address to: {network}")

        if ip_version == "ipv6":
            config['network']['interface_1_v6_ip_address'] = ip_address

        logger.debug(f"INFO - Updated ip address to: {ip_address}")

        # Write the updated config back to the YAML file
        with open(GLOBAL_CONFIG_FILE_PATH, 'w') as file:
            yaml.safe_dump(config, file, default_flow_style=False)

        logger.debug("INFO - Ip address replacement successful.")
        return True

    except Exception as e:
        logger.error(f"ERROR - Error occurred while replacing ip address in the global_config.yaml file: {str(e)}")
        return False
