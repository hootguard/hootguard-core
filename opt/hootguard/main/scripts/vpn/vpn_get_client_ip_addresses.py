# Script Name: vpn_get_client_ip_addresses.py
# Version: 0.1
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script retrieves the IPv4 and IPv6 addresses for a specific VPN client from the `all_vpn_clients` table in the SQLite database.
# If the client is found, it returns the corresponding IP addresses; if not, it returns (None, None).
# The script also logs the success or failure of the operation using a global logger.

import sqlite3
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def get_client_ips(client_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()

        # Prepare and execute the query to fetch the client's IP addresses
        query = "SELECT ipv4_address, ipv6_address FROM all_vpn_clients WHERE client_name = ?"
        cursor.execute(query, (client_name,))

        # Fetch the result (assuming client_name is unique)
        client_ips = cursor.fetchone()

        # Close the database connection
        conn.close()

        if client_ips:
            ipv4_address, ipv6_address = client_ips
            logger.debug(f"Successfully retrieved IP addresses for client '{client_name}'")
            return ipv4_address, ipv6_address
        else:
            logger.debug(f"No client found with the name '{client_name}'")
            return None, None

    except sqlite3.Error as e:
        logger.debug(f"An error occurred while fetching IP addresses for client '{client_name}': {e}")
        return None, None
