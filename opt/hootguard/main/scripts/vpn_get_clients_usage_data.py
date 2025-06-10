# Script Name: vpn_get_clients_usage_data.py
# Version: 0.3
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script retrieves real-time VPN usage data for all WireGuard clients and links the data to
# the corresponding client names by parsing the WireGuard configuration files. The script fetches
# information such as data received, data sent, and the time of the last handshake for each client.
# It outputs the data in JSON format, making it suitable for integration with a Flask application or
# other systems that require VPN usage statistics.
#
# Logging is implemented directly within this script because the script is executed via the 
# `vpn_usage_data_json = subprocess.check_output(['sudo', '/usr/bin/python3', '/opt/hootguard/main/scripts/vpn_get_clients_usage_data.py'], text=True)`
# command in the Flask blueprint. This approach avoids the use of relative imports, which would be problematic 
# when running the script as a standalone executable using subprocess. Embedding the logging configuration in 
# this script ensures that the logging mechanism works consistently without needing external imports.

import subprocess
import re
import json
import os
import logging

# Configure logging
logger = logging.getLogger('HGLog')
log_level = 'INFO'

# Check if the logger already has handlers (prevents adding duplicate handlers)
if not logger.hasHandlers():
    logger.setLevel(getattr(logging, log_level, logging.INFO))

    # Create a file handler
    file_handler = logging.FileHandler('/var/log/hootguard_system.log')
    file_handler.setLevel(getattr(logging, log_level, logging.INFO))

    # Create a logging format that includes the script/module name
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s - %(module)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Optionally, add a console handler to also output logs to the console (for development/debugging)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level, logging.INFO))  # Set console handler log level dynamically
    console_handler.setFormatter(formatter)

    # Add the console handler to the logger
    logger.addHandler(console_handler)

# Define WireGuard configuration files globally
config_files = ['/etc/wireguard/wg0.conf', '/etc/wireguard/wg1.conf']

# Function to parse WireGuard config and build a mapping of public keys to client names
def get_client_name_mapping(config_files):
    logger.debug("Starting to parse WireGuard configuration files.")
    client_mapping = {}
    for config_file in config_files:
        try:
            with open(config_file, 'r') as file:
                content = file.read()

                # Regex to match the client name and public key between the begin and end markers
                matches = re.findall(r"### begin (.+?) ###.*?PublicKey = (.+?)\n", content, re.DOTALL)
                for match in matches:
                    client_name, public_key = match
                    client_mapping[public_key.strip()] = client_name.strip()
        except FileNotFoundError as e:
            logger.debug(f"Config file not found: {config_file}. Error: {e}")
        except Exception as e:
            logger.debug(f"Error reading config file {config_file}. Error: {e}")

    #logger.debug("Completed parsing of WireGuard configuration files.")
    return client_mapping

# Function to fetch WireGuard data in real-time and link with client names
def get_vpn_data(client_mapping):
    logger.debug("Fetching real-time VPN data using 'wg' command.")
    vpn_data = {}
    try:
        wg_output = subprocess.check_output(['/usr/bin/sudo', '/usr/local/bin/hootguard', 'wg-show'], text=True)
        
        current_peer = None

        for line in wg_output.splitlines():
            if line.startswith("peer:"):
                current_peer = line.split()[1]
                client_name = client_mapping.get(current_peer, 'Unknown')  # Lookup client name by public key
                vpn_data[client_name] = {'received': '0 KiB', 'sent': '0 KiB', 'last_seen': 'N/A'}
            elif "transfer" in line:
                transfer_data = line.split(", ")
                vpn_data[client_name]['received'] = transfer_data[0].split()[1] + ' ' + transfer_data[0].split()[2]  # Extract data received with unit
                vpn_data[client_name]['sent'] = transfer_data[1].split()[0] + ' ' + transfer_data[1].split()[1]  # Extract data sent with unit
            elif "latest handshake" in line:
                handshake = line.split(": ")[1]  # Extract last seen
                if handshake == "(none)":
                    vpn_data[client_name]['last_seen'] = "Not connected"
                else:
                    vpn_data[client_name]['last_seen'] = handshake

        logger.debug("Successfully fetched VPN data.")
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to execute 'wg' command. Error: {e}")
    except Exception as e:
        logger.debug(f"Unhandled exception while fetching VPN data. Error: {e}")
    return vpn_data

# Main function to gather VPN usage data for Flask
def get_vpn_usage_data():
    logger.debug("Starting VPN usage data gathering.")
    client_mapping = get_client_name_mapping(config_files)
    vpn_data = get_vpn_data(client_mapping)
    logger.debug("Completed VPN usage data gathering.")
    return vpn_data

# Output the VPN data as JSON
if __name__ == '__main__':
    logger.debug("Script execution started.")
    vpn_data = get_vpn_usage_data()
    logger.debug("VPN usage data gathered. Outputting JSON.")
    print(json.dumps(vpn_data))  # Output the dictionary as a JSON string
    logger.debug("Script execution completed.")
