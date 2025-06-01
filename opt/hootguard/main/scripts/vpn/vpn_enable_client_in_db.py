# Script Name: vpn_enable_client_in_db.py
# Version: 0.1
# Author: HootGuard
# Date: 5. October 2024

# Description:
# This script updates the SQLite database to set the `vpn_status` field to 1 (enabled) for a given VPN client.
# It is used to mark the client as active in the `all_vpn_clients` table.

import sqlite3
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def enable_client_in_db(client_name):
    """Update the database to set the vpn_status to 1 (enabled) for the client."""
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()

        # Update the vpn_status to 1 (enabled)
        cursor.execute("""
            UPDATE all_vpn_clients
            SET vpn_status = 1
            WHERE client_name = ?
        """, (client_name,))

        conn.commit()
        conn.close()

        logger.debug(f"VPN client {client_name} marked as enabled in the database.")
        return True
    except Exception as e:
        logger.debug(f"Failed to enable VPN client {client_name} in the database: {str(e)}")
        return False
