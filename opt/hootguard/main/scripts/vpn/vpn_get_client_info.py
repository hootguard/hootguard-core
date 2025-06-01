# Script Name: vpn_get_client_info.py
# Version: 0.1
# Author: HootGuard
# Date: 4. October 2024

# Description:
# This script retrieves the `wg_interface` and `vpn_type` for a given client name from the SQLite database.

import sqlite3
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def get_client_info(client_name):
    """Retrieve the wg_interface and vpn_type from the database based on the client name."""
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()

        # Query to retrieve wg_interface and vpn_type
        cursor.execute("""
            SELECT wg_interface, vpn_type FROM all_vpn_clients WHERE client_name = ?;
        """, (client_name,))
        result = cursor.fetchone()

        conn.close()

        if result:
            wg_interface, vpn_type = result
            return wg_interface, vpn_type
        else:
            logger.debug(f"Client {client_name} not found in the database.")
            return None, None
    except Exception as e:
        logger.debug(f"Failed to retrieve client info for {client_name}: {str(e)}")
        return None, None
