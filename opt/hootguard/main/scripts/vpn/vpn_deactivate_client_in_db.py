# Script Name: vpn_deactivate_client_in_db.py
# Version: 0.1
# Author: HootGuard
# Date: 5. October 2024

# Description:
# This script updates the SQLite database to set the `vpn_status` field to 0 (disabled) for a given VPN client.
# This is used to mark the client as deactivated in the `all_vpn_clients` table, ensuring that the client is no longer active.

# Usage:
# Call the function 'deactivate_client_in_db(client_name)' with the VPN client's name as a parameter. 
# The function connects to the database specified by `VPN_CLIENTS_DB_PATH`, updates the client's `vpn_status` to 0 
# in the `all_vpn_clients` table, and commits the changes. Returns True if the operation is successful, 
# and False if an error occurs during the process.

# Change Log:
# 5. October 2024
# Initial version for updating the VPN client's status to 'disabled' in the database.

import sqlite3
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def deactivate_client_in_db(client_name):
    """Update the database to set the vpn_status to 0 (disabled) for the client."""
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()

        # Update the vpn_status to 0 (deactivated)
        cursor.execute("""
            UPDATE all_vpn_clients
            SET vpn_status = 0
            WHERE client_name = ?
        """, (client_name,))

        conn.commit()
        conn.close()

        logger.debug(f"VPN client {client_name} marked as deactivated in the database.")
        return True
    except Exception as e:
        logger.debug(f"Failed to deactivate VPN client {client_name} in the database: {str(e)}")
        return False
